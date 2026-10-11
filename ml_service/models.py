# Xerolux 2026
# SPDX-License-Identifier: MIT
import math
import random
import threading
from collections import deque
from dataclasses import dataclass
from typing import Any

import torch
from torch import nn

from .config import config


class ResidualBlock(nn.Module):
    def __init__(self, dim: int, dropout_rate: float = 0.1):
        super().__init__()
        self.block = nn.Sequential(
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
            nn.LeakyReLU(0.1),
            nn.Dropout(dropout_rate),
            nn.Linear(dim, dim),
            nn.LayerNorm(dim),
        )
        self.activation = nn.LeakyReLU(0.1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.activation(x + self.block(x))


class Autoencoder(nn.Module):
    def __init__(
        self,
        input_dim: int,
        hidden_dim: int | None = None,
        latent_dim: int | None = None,
        dropout_rate: float = 0.15,
    ):
        super().__init__()
        hidden_dim = hidden_dim or config.ae_hidden_dim
        latent_dim = latent_dim or config.ae_latent_dim

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.LeakyReLU(0.1),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.LeakyReLU(0.1),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim // 2, latent_dim),
            nn.LeakyReLU(0.1),
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim // 2),
            nn.LayerNorm(hidden_dim // 2),
            nn.LeakyReLU(0.1),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim // 2, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.LeakyReLU(0.1),
            ResidualBlock(hidden_dim, dropout_rate),
            nn.Linear(hidden_dim, input_dim),
        )
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x))

    def encode(self, x: torch.Tensor) -> torch.Tensor:
        return self.encoder(x)


class OnlineStandardScaler:
    def __init__(self):
        self._lock = threading.Lock()
        self.n: dict[str, int] = {}
        self.means: dict[str, float] = {}
        self.m2: dict[str, float] = {}
        self.vars: dict[str, float] = {}

    def partial_fit(self, data: dict[str, Any]) -> None:
        with self._lock:
            for key, value in data.items():
                if not isinstance(value, (int, float)) or (
                    isinstance(value, float) and math.isnan(value)
                ):
                    continue
                if key not in self.n:
                    self.n[key] = 0
                    self.means[key] = 0.0
                    self.m2[key] = 0.0
                    self.vars[key] = 0.0
                self.n[key] += 1
                count = self.n[key]
                delta = value - self.means[key]
                self.means[key] += delta / count
                delta2 = value - self.means[key]
                if key not in self.m2:
                    self.m2[key] = 0.0
                if key not in self.vars:
                    self.vars[key] = 0.0
                self.m2[key] += delta * delta2
                self.vars[key] = self.m2[key] / count if count > 1 else 0.0

    def transform(self, data: dict[str, Any], feature_order: list[str]) -> list[float]:
        with self._lock:
            result = []
            for key in feature_order:
                value = data.get(key, 0.0)
                if not isinstance(value, (int, float)):
                    value = 0.0
                mean = self.means.get(key, 0.0)
                std = self.vars.get(key, 0.0) ** 0.5
                if std > 1e-6:
                    result.append((value - mean) / std)
                else:
                    result.append(0.0)
            return result

    def get_stats(self) -> dict[str, dict[str, float]]:
        with self._lock:
            return {k: {"mean": self.means[k], "var": self.vars[k]} for k in self.means}


class ReplayBuffer:
    def __init__(self, capacity: int = 500):
        self._buffer = deque(maxlen=capacity)
        self._lock = threading.Lock()

    def add(self, tensor: torch.Tensor):
        with self._lock:
            self._buffer.append(tensor.clone().detach())

    def sample(self, batch_size: int) -> torch.Tensor | None:
        with self._lock:
            if len(self._buffer) < batch_size:
                return None
            samples = random.sample(list(self._buffer), batch_size)
            return torch.cat(samples, dim=0)

    def __len__(self):
        return len(self._buffer)


@dataclass
class AnomalyResult:
    score: float
    is_anomaly: bool
    mode: str
    features: dict[str, float]
    top_contributors: list[dict[str, Any]]
    reconstruction_error: float
    per_feature_errors: dict[str, float]


class AutoencoderModel:
    def __init__(
        self,
        hidden_dim: int | None = None,
        latent_dim: int | None = None,
        learning_rate: float | None = None,
        train_steps: int | None = None,
        ema_alpha: float | None = None,
        dropout_rate: float = 0.15,
        noise_std: float = 0.05,
        gradient_clip: float = 1.0,
    ):
        self.hidden_dim = hidden_dim or config.ae_hidden_dim
        self.latent_dim = latent_dim or config.ae_latent_dim
        self.learning_rate = learning_rate or config.ae_learning_rate
        self.train_steps = train_steps or config.ae_train_steps
        self.ema_alpha = ema_alpha or config.ae_ema_alpha
        self.dropout_rate = dropout_rate
        self.noise_std = noise_std
        self.gradient_clip = gradient_clip

        self.scaler = OnlineStandardScaler()
        self.feature_order: list[str] = []
        self.net: Autoencoder | None = None
        self.optimizer: torch.optim.Adam | None = None
        self.scheduler: torch.optim.lr_scheduler.ReduceLROnPlateau | None = None
        self.criterion = nn.HuberLoss(delta=1.0, reduction="mean")

        self.replay_buffer = ReplayBuffer(capacity=500)
        self.min_replay_batch = 16

        self.ema_loss: float | None = None
        self.ema_loss_sq: float | None = None
        self.sample_count: int = 0
        self.total_steps: int = 0
        self._lock = threading.RLock()

    def _ensure_net(self, input_dim: int) -> None:
        if self.net is None:
            self.net = Autoencoder(
                input_dim,
                self.hidden_dim,
                self.latent_dim,
                self.dropout_rate,
            )
            self.optimizer = torch.optim.Adam(
                self.net.parameters(), lr=self.learning_rate, weight_decay=1e-5
            )
            self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer, mode="min", factor=0.5, patience=200, min_lr=1e-6
            )

    def _prepare_input(self, data: dict[str, Any]) -> torch.Tensor:
        numeric_data = {
            k: v
            for k, v in data.items()
            if isinstance(v, (int, float))
            and not (isinstance(v, float) and math.isnan(v))
        }
        if not self.feature_order:
            with self._lock:
                if not self.feature_order:
                    self.feature_order = sorted(numeric_data.keys())
        scaled = self.scaler.transform(numeric_data, self.feature_order)
        return torch.tensor([scaled], dtype=torch.float32)

    def score_one(self, data: dict[str, Any]) -> float:
        if not self.feature_order or self.sample_count < 50:
            return 0.0

        with self._lock:
            self._ensure_net(len(self.feature_order))
            self.net.eval()

            with torch.no_grad():
                x = self._prepare_input(data)
                x_hat = self.net(x)
                errors = (x - x_hat) ** 2
                mse = errors.mean().item()

        if self.ema_loss is None:
            return 0.0

        return self._compute_score(mse)

    def score_one_detailed(self, data: dict[str, Any]) -> AnomalyResult:
        if not self.feature_order or self.sample_count < 50:
            return AnomalyResult(
                score=0.0,
                is_anomaly=False,
                mode="unknown",
                features=data,
                top_contributors=[],
                reconstruction_error=0.0,
                per_feature_errors={},
            )

        with self._lock:
            self._ensure_net(len(self.feature_order))
            self.net.eval()

            with torch.no_grad():
                x = self._prepare_input(data)
                x_hat = self.net(x)
                errors = (x - x_hat) ** 2
                mse = errors.mean().item()

                per_feature = {}
                if len(self.feature_order) == x.shape[1]:
                    err_values = errors.squeeze(0).tolist()
                    per_feature = {
                        feat: err_values[i] for i, feat in enumerate(self.feature_order)
                    }

        score = self._compute_score(mse)

        top_contributors = self._rank_features(data, per_feature)

        return AnomalyResult(
            score=score,
            is_anomaly=score > 0.5,
            mode="unknown",
            features=data,
            top_contributors=top_contributors,
            reconstruction_error=mse,
            per_feature_errors=per_feature,
        )

    def _compute_score(self, mse: float) -> float:
        if self.ema_loss is None:
            return 0.0

        ema_var = max(self.ema_loss_sq - self.ema_loss**2, 0.0)
        ema_std = ema_var**0.5

        if ema_std < 1e-8:
            score = min(mse / (self.ema_loss + 1e-8) / 3.0, 1.0)
        else:
            z = (mse - self.ema_loss) / ema_std
            z_shifted = z - 2.0
            score = 1.0 / (1.0 + math.exp(-z_shifted))

        return float(max(0.0, min(1.0, score)))

    def _rank_features(
        self, data: dict[str, Any], per_feature_errors: dict[str, float]
    ) -> list[dict[str, Any]]:
        scaler = self.scaler
        if not scaler.means or not per_feature_errors:
            return []

        contributions = []
        for feat, recon_err in per_feature_errors.items():
            if feat in scaler.means:
                value = data.get(feat, 0.0)
                if isinstance(value, (int, float)):
                    mean = scaler.means[feat]
                    std = scaler.vars.get(feat, 0.0) ** 0.5
                    z_score = abs(value - mean) / std if std > 1e-6 else 0.0
                    combined = 0.6 * z_score + 0.4 * (
                        recon_err / (self.ema_loss + 1e-8)
                    )
                    contributions.append(
                        {
                            "feature": feat,
                            "score": float(combined),
                            "z_score": float(z_score),
                            "recon_error": float(recon_err),
                            "value": float(value),
                            "mean": float(mean),
                        }
                    )

        contributions.sort(key=lambda x: x["score"], reverse=True)
        return contributions[:3]

    def learn_one(self, data: dict[str, Any]) -> float:
        with self._lock:
            self.sample_count += 1
        self.scaler.partial_fit(data)

        numeric_data = {
            k: v
            for k, v in data.items()
            if isinstance(v, (int, float))
            and not (isinstance(v, float) and math.isnan(v))
        }

        if not self.feature_order:
            with self._lock:
                if not self.feature_order:
                    self.feature_order = sorted(numeric_data.keys())

        with self._lock:
            self._ensure_net(len(self.feature_order))
            self.net.train()
            x = self._prepare_input(data)

            self.replay_buffer.add(x)

            noise_scale = self.noise_std * max(
                0.1, 1.0 - min(self.sample_count / 500.0, 1.0)
            )
            if noise_scale > 0.01:
                x_noisy = x + torch.randn_like(x) * noise_scale
            else:
                x_noisy = x

            self.optimizer.zero_grad()
            x_hat = self.net(x_noisy)
            loss = self.criterion(x_hat, x)
            loss.backward()
            nn.utils.clip_grad_norm_(self.net.parameters(), self.gradient_clip)
            self.optimizer.step()

            replay_batch = self.replay_buffer.sample(self.min_replay_batch)
            if replay_batch is not None:
                replay_noise = torch.randn_like(replay_batch) * max(
                    noise_scale * 0.5, 0.01
                )
                self.optimizer.zero_grad()
                x_hat_r = self.net(replay_batch + replay_noise)
                replay_loss = self.criterion(x_hat_r, replay_batch)
                replay_loss.backward()
                nn.utils.clip_grad_norm_(self.net.parameters(), self.gradient_clip)
                self.optimizer.step()
                loss_val = (loss.item() + replay_loss.item()) / 2.0
            else:
                loss_val = loss.item()

            self.total_steps += 1
            if self.scheduler:
                self.scheduler.step(loss_val)

        if self.ema_loss is None:
            self.ema_loss = loss_val
            self.ema_loss_sq = loss_val**2
        else:
            alpha = self.ema_alpha
            if self.sample_count < 100:
                alpha = min(alpha * 2, 0.1)
            self.ema_loss = (1 - alpha) * self.ema_loss + alpha * loss_val
            self.ema_loss_sq = (1 - alpha) * self.ema_loss_sq + alpha * (loss_val**2)

        return loss_val

    def get_top_features(
        self, data: dict[str, Any], n: int = 3
    ) -> list[dict[str, Any]]:
        result = self.score_one_detailed(data)
        return result.top_contributors[:n]

    def get_state(self) -> dict[str, Any]:
        return {
            "sample_count": self.sample_count,
            "total_steps": self.total_steps,
            "feature_order": self.feature_order,
            "scaler_means": dict(self.scaler.means),
            "scaler_vars": dict(self.scaler.vars),
            "scaler_n": dict(self.scaler.n),
            "scaler_m2": dict(self.scaler.m2),
            "ema_loss": self.ema_loss,
            "ema_loss_sq": self.ema_loss_sq,
            "net_state": self.net.state_dict() if self.net else None,
            "optimizer_state": self.optimizer.state_dict() if self.optimizer else None,
            "hidden_dim": self.hidden_dim,
            "latent_dim": self.latent_dim,
            "learning_rate": self.learning_rate,
            "dropout_rate": self.dropout_rate,
            "noise_std": self.noise_std,
            "gradient_clip": self.gradient_clip,
        }

    def load_state(self, state: dict[str, Any]) -> None:
        self.sample_count = state.get("sample_count", 0)
        self.total_steps = state.get("total_steps", 0)
        self.feature_order = state.get("feature_order", [])
        self.scaler.means = state.get("scaler_means", {})
        self.scaler.vars = state.get("scaler_vars", {})
        scaler_n = state.get("scaler_n", {})
        if isinstance(scaler_n, int):
            for key in self.scaler.means:
                self.scaler.n[key] = scaler_n
        else:
            self.scaler.n = scaler_n
        self.scaler.m2 = state.get("scaler_m2", {})
        self.ema_loss = state.get("ema_loss")
        self.ema_loss_sq = state.get("ema_loss_sq")

        net_state = state.get("net_state")
        if net_state and self.feature_order:
            self._ensure_net(len(self.feature_order))
            self.net.load_state_dict(net_state)

        opt_state = state.get("optimizer_state")
        if opt_state and self.optimizer:
            try:
                self.optimizer.load_state_dict(opt_state)
            except ValueError:
                pass


def create_model() -> AutoencoderModel:
    return AutoencoderModel(
        hidden_dim=config.ae_hidden_dim,
        latent_dim=config.ae_latent_dim,
        learning_rate=config.ae_learning_rate,
        train_steps=config.ae_train_steps,
        ema_alpha=config.ae_ema_alpha,
    )
