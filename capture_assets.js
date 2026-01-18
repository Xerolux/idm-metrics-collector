const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const net = require('net');
const ffmpegPath = require('ffmpeg-static');

// Constants
const SCREENSHOT_DIR = path.join(__dirname, 'docs', 'screenshots');
const IMAGES_DIR = path.join(__dirname, 'docs', 'images');
const VIDEO_DIR = path.join(__dirname, 'temp_videos');

// Ensure directories exist
[SCREENSHOT_DIR, IMAGES_DIR, VIDEO_DIR].forEach(dir => {
    if (fs.existsSync(dir)) {
        // Clean up old files
        fs.rmSync(dir, { recursive: true, force: true });
    }
    fs.mkdirSync(dir, { recursive: true });
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
    webdav_password: 'super_secret_password_123', // Will be blurred
    admin_password_hash: 'hash',
    idm_host: '192.168.1.100',
    metrics_url: 'http://localhost:8428',
    backup: {
        interval: 24,
        retention: 7,
        path: '/backups'
    }
};

const MOCK_VERSION = { version: '0.6.0' };
// CRITICAL: Ensure must_change_password is false to bypass the forced change screen
const MOCK_AUTH = { authenticated: true, must_change_password: false };

async function startFrontend() {
    console.log('Starting Frontend...');
    // We assume npm install is done.
    const vite = spawn('npx', ['vite', '--port', '5173'], {
        cwd: path.join(__dirname, 'frontend'),
        shell: true,
        env: { ...process.env, VITE_API_BASE_URL: 'http://localhost:5173/api' } // Mock API base? Vite proxies usually.
    });

    vite.stdout.on('data', (data) => {
        // console.log(`Vite: ${data}`)
    });
    vite.stderr.on('data', (data) => {
        // console.error(`Vite Err: ${data}`)
    });

    // Wait for server to be ready
    console.log("Waiting for Vite to spin up...");
    // Increased timeout to ensure it spins up in slower environments
    await new Promise(resolve => setTimeout(resolve, 15000));
    return vite;
}

async function capture() {
    let viteProcess;
    let browser;

    try {
        // Check if port 5173 is already in use, if so assume external server
        const isPortInUse = await new Promise(resolve => {
            const client = new net.Socket();
            client.once('connect', () => {
                client.destroy();
                resolve(true);
            });
            client.once('error', () => {
                client.destroy();
                resolve(false);
            });
            client.connect(5173, 'localhost');
        });

        if (!isPortInUse) {
             viteProcess = await startFrontend();
        } else {
            console.log("Port 5173 in use, assuming external server running.");
        }

        browser = await chromium.launch({
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        // Create a context with video recording for GIFs
        const context = await browser.newContext({
            viewport: { width: 1440, height: 900 }, // Larger for better detail
            recordVideo: { dir: VIDEO_DIR, size: { width: 1440, height: 900 } },
            colorScheme: 'dark'
        });

        const page = await context.newPage();

        // --- MOCKING ROUTES ---
        // We intercept *everything* under /api to return our mock data.

        // Auth Check
        await page.route('**/api/auth/check', async route => {
            await route.fulfill({ json: MOCK_AUTH });
        });

        // Login
        await page.route('**/api/login', async route => {
            await route.fulfill({ json: { success: true } });
        });

        // Setup
        await page.route('**/api/setup', async route => {
            await route.fulfill({ json: { success: true } });
        });

        // Main Data
        await page.route('**/api/data', async route => {
            await route.fulfill({ json: MOCK_DATA });
        });

        // Version
        await page.route('**/api/version', async route => {
            await route.fulfill({ json: MOCK_VERSION });
        });

        // Config
        await page.route('**/api/config', async route => {
            await route.fulfill({ json: MOCK_CONFIG });
        });

        // Logs (return some dummy logs)
        await page.route('**/api/logs', async route => {
            await route.fulfill({ json: { logs: [
                "2023-10-27 10:00:01 INFO: System started",
                "2023-10-27 10:00:02 INFO: Connected to IDM at 192.168.1.100",
                "2023-10-27 10:05:00 INFO: Metrics pushed successfully"
            ] } });
        });

        // Base URL for navigation (Vite dev server)
        const BASE_URL = 'http://localhost:5173/static';

        // Inject CSS for blurring sensitive data across the entire session
        await page.addInitScript(() => {
            const style = document.createElement('style');
            style.innerHTML = `
                input[type="password"],
                input[name*="key"],
                input[name*="token"],
                input[name*="secret"],
                .p-password-input,
                .sensitive-data
                {
                    filter: blur(5px) !important;
                    opacity: 0.7;
                }
            `;
            document.head.appendChild(style);
        });

        // --- SCENARIO 0: Setup Screen (Static Screenshot) ---
        console.log('Capturing Setup...');
        await page.goto(`${BASE_URL}/setup`);
        await page.waitForTimeout(1000);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '00_setup.png') });

        // --- SCENARIO 1: Login Screen (Static Screenshot) ---
        console.log('Capturing Login...');
        // Mock unauthenticated state temporarily
        await page.route('**/api/auth/check', async route => {
            await route.fulfill({ json: { authenticated: false } });
        });

        await page.goto(`${BASE_URL}/login`);
        await page.waitForTimeout(1000); // Wait for animation
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_login.png') });

        // --- SCENARIO 2: Main Application Walkthrough (Video & Screenshots) ---
        console.log('Capturing Application Flow...');

        // Restore Authenticated State
        await page.unroute('**/api/auth/check');
        await page.route('**/api/auth/check', async route => {
             await route.fulfill({ json: { authenticated: true, must_change_password: false } });
        });

        // 1. Dashboard
        await page.goto(`${BASE_URL}/`);
        await page.waitForTimeout(4000); // Linger on dashboard
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_dashboard.png') });

        // Simulate some live data updates for the video effect
        let tempData = { ...MOCK_DATA };
        for(let i=0; i<5; i++) {
            tempData.temp_heat_pump_flow += (Math.random() - 0.5);
             await page.evaluate((data) => {
                 // Triggering a fake event if we could, but the poller will just pick up the new mocked data
            }, tempData);
            // Update the mock response for the polling
             await page.unroute('**/api/data');
             await page.route('**/api/data', async route => {
                await route.fulfill({ json: tempData });
             });
            await page.waitForTimeout(200);
        }

        // 2. Control
        await page.goto(`${BASE_URL}/control`);
        await page.waitForTimeout(2500);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_control.png') });

        // 3. Schedule
        await page.goto(`${BASE_URL}/schedule`);
        await page.waitForTimeout(2500);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_schedule.png') });

        // 4. Alerts
        await page.goto(`${BASE_URL}/alerts`);
        await page.waitForTimeout(2500);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_alerts.png') });

        // 5. Config (Blurred)
        await page.goto(`${BASE_URL}/config`);
        await page.waitForTimeout(3000); // Give time to see the blur
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_config.png') });

        // 6. Logs
        await page.goto(`${BASE_URL}/logs`);
        await page.waitForTimeout(2500);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '07_logs.png') });

        // 7. Tools
        await page.goto(`${BASE_URL}/tools`);
        await page.waitForTimeout(2500);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '08_tools.png') });

        // 8. About
        await page.goto(`${BASE_URL}/about`);
        await page.waitForTimeout(2500);
        await page.screenshot({ path: path.join(SCREENSHOT_DIR, '09_about.png') });

        // Go back to dashboard for a clean loop end
        await page.goto(`${BASE_URL}/`);
        await page.waitForTimeout(2000);

        // Close to save video
        await context.close();
        await browser.close();
        if (viteProcess) viteProcess.kill();

        // Convert Video to GIF
        const videoFile = fs.readdirSync(VIDEO_DIR).find(f => f.endsWith('.webm'));
        if (videoFile) {
            const inputPath = path.join(VIDEO_DIR, videoFile);
            const outputPath = path.join(IMAGES_DIR, 'demo.gif');

            console.log(`Converting ${inputPath} to ${outputPath}...`);

            // ffmpeg to convert webm to gif
            // optimized filters for better quality/size ratio
            const ffmpeg = spawn(ffmpegPath, [
                '-y',
                '-i', inputPath,
                '-vf', 'fps=10,scale=1000:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse',
                '-loop', '0',
                outputPath
            ]);

            ffmpeg.on('close', (code) => {
                console.log(`FFmpeg finished with code ${code}`);
                if (code === 0) {
                     console.log("Assets generated successfully!");
                     process.exit(0);
                } else {
                     process.exit(code);
                }
            });
        } else {
            console.log("No video file found.");
            process.exit(1);
        }

    } catch (error) {
        console.error("Error during capture:", error);
        if (viteProcess) viteProcess.kill();
        if (browser) await browser.close();
        process.exit(1);
    }
}

capture();
