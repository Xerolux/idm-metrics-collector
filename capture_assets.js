const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Constants
const SCREENSHOT_DIR = path.join(__dirname, 'docs', 'screenshots');
const IMAGES_DIR = path.join(__dirname, 'docs', 'images');
const VIDEO_DIR = path.join(__dirname, 'temp_videos');

// Ensure directories exist
[SCREENSHOT_DIR, IMAGES_DIR, VIDEO_DIR].forEach(dir => {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
});

// Mock Data
const MOCK_DATA = {
    temp_outside: 12.5,
    temp_heat_pump_flow: 35.2,
    temp_heat_pump_return: 30.1,
    temp_heat_storage: 45.0,
    temp_water_heater_top: 52.0,
    power_current_draw: 2.1,
    status_pump_heat_circuit: true,
    status_pump_heat_source: true,
    status_compressor: true,
    status_request_heating: true,
    status_request_water: false,
    operating_mode: 'heating',
    error_code: 0,
    error_text: 'No Error'
};

const MOCK_CONFIG = {
    webdav_url: 'https://webdav.example.com',
    webdav_username: 'user',
    webdav_password: 'secret_password',
    admin_password_hash: 'hash',
    idm_host: '192.168.1.100',
    metrics_url: 'http://localhost:8428'
};

const MOCK_VERSION = { version: '0.6.0' };
const MOCK_AUTH = { authenticated: true, must_change_password: false };

async function startFrontend() {
    console.log('Starting Frontend...');
    const vite = spawn('npx', ['vite', '--port', '5173'], {
        cwd: path.join(__dirname, 'frontend'),
        shell: true
    });

    vite.stdout.on('data', (data) => console.log(`Vite: ${data}`));
    vite.stderr.on('data', (data) => console.error(`Vite Err: ${data}`));

    // Wait for server to be ready
    await new Promise(resolve => setTimeout(resolve, 5000));
    return vite;
}

async function capture() {
    const viteProcess = await startFrontend();
    const browser = await chromium.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox'] // Add these for container environments
    });

    // Create a context with video recording for GIFs
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 },
        recordVideo: { dir: VIDEO_DIR, size: { width: 1280, height: 800 } }
        // Removed baseURL to avoid confusion with redirects
    });

    const page = await context.newPage();

    // Mock API Routes
    // Note: We need to intercept requests to the backend API, which in dev mode are proxied.
    // Since we are mocking, we just intercept the requests Playwright sees.
    // The frontend makes requests to /api/..., which map to http://localhost:5173/api/...
    // So we can just route **/api/**

    await page.route('**/api/auth/check', async route => {
        await route.fulfill({ json: MOCK_AUTH });
    });

    await page.route('**/api/login', async route => {
        await route.fulfill({ json: { success: true } });
    });

    await page.route('**/api/data', async route => {
        await route.fulfill({ json: MOCK_DATA });
    });

    await page.route('**/api/version', async route => {
        await route.fulfill({ json: MOCK_VERSION });
    });

    await page.route('**/api/config', async route => {
        await route.fulfill({ json: MOCK_CONFIG });
    });

    // Base URL for navigation
    const BASE_URL = 'http://localhost:5173/static';

    // 1. Login Screen
    // Mock unauthenticated state for this shot
    await page.route('**/api/auth/check', async route => {
        await route.fulfill({ json: { authenticated: false } });
    });

    // Navigate to /static/login
    await page.goto(`${BASE_URL}/login`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_login.png') });

    // Restore Auth
    await page.unroute('**/api/auth/check');
    await page.route('**/api/auth/check', async route => {
         await route.fulfill({ json: { authenticated: true, must_change_password: false } });
    });

    // 2. Dashboard
    // Navigate to /static/
    await page.goto(`${BASE_URL}/`);
    await page.waitForTimeout(2000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_dashboard.png') });

    // Capture Video for Dashboard GIF
    let tempData = { ...MOCK_DATA };
    await page.route('**/api/data', async route => {
        tempData.temp_heat_pump_flow += (Math.random() - 0.5);
        await route.fulfill({ json: tempData });
    });

    await page.waitForTimeout(5000);

    // 3. Control
    await page.goto(`${BASE_URL}/control`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_control.png') });

    // 4. Schedule
    await page.goto(`${BASE_URL}/schedule`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_schedule.png') });

    // 5. Alerts
    await page.goto(`${BASE_URL}/alerts`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_alerts.png') });

    // 6. Config (Blur sensitive)
    await page.goto(`${BASE_URL}/config`);
    await page.waitForTimeout(1000);

    await page.addStyleTag({
        content: `
            input[type="password"],
            input[name*="key"],
            input[name*="token"],
            .p-password-input
            {
                filter: blur(5px) !important;
                opacity: 0.7;
            }
        `
    });
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_config.png') });

    // 7. Logs
    await page.goto(`${BASE_URL}/logs`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '07_logs.png') });

    // 8. Tools
    await page.goto(`${BASE_URL}/tools`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '08_tools.png') });

    // 9. About
    await page.goto(`${BASE_URL}/about`);
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, '09_about.png') });

    // Close to save video
    await context.close();
    await browser.close();

    viteProcess.kill();

    // Convert Video to GIF
    const videoFile = fs.readdirSync(VIDEO_DIR).find(f => f.endsWith('.webm'));
    if (videoFile) {
        const inputPath = path.join(VIDEO_DIR, videoFile);
        const outputPath = path.join(IMAGES_DIR, 'demo.gif');

        console.log(`Converting ${inputPath} to ${outputPath}...`);

        const ffmpeg = spawn('ffmpeg', [
            '-y',
            '-i', inputPath,
            '-vf', 'fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
            '-loop', '0',
            outputPath
        ]);

        ffmpeg.on('close', (code) => {
            console.log(`FFmpeg finished with code ${code}`);
            process.exit(code);
        });
    } else {
        console.log("No video file found.");
        process.exit(1);
    }
}

capture().catch(err => {
    console.error(err);
    process.exit(1);
});
