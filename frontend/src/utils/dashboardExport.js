/**
 * Dashboard Export Utility
 *
 * Exports dashboards as PNG or PDF using html2canvas and jsPDF
 */

import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';

/**
 * Export a DOM element as PNG image
 * @param {HTMLElement} element - The element to capture
 * @param {Object} options - Export options
 * @returns {Promise<Blob>} - PNG image blob
 */
export async function exportAsPNG(element, options = {}) {
    const {
        scale = 2, // Higher scale = better quality
        backgroundColor = '#ffffff',
        logging = false,
    } = options;

    try {
        const canvas = await html2canvas(element, {
            scale,
            backgroundColor,
            logging,
            useCORS: true, // Allow cross-origin images
            allowTaint: true,
        });

        return new Promise((resolve) => {
            canvas.toBlob((blob) => {
                resolve(blob);
            }, 'image/png');
        });
    } catch (error) {
        console.error('PNG export failed:', error);
        throw new Error('Export fehlgeschlagen: ' + error.message);
    }
}

/**
 * Export a DOM element as PDF
 * @param {HTMLElement} element - The element to capture
 * @param {Object} options - Export options
 * @returns {Promise<Blob>} - PDF document blob
 */
export async function exportAsPDF(element, options = {}) {
    const {
        // filename = 'dashboard',
        format = 'a4',
        orientation = 'landscape',
        scale = 2,
        quality = 0.95,
    } = options;

    try {
        // First capture as canvas
        const canvas = await html2canvas(element, {
            scale,
            logging: false,
            useCORS: true,
            allowTaint: true,
        });

        // Calculate PDF dimensions
        const imgWidth = canvas.width;
        const imgHeight = canvas.height;

        // A4 landscape dimensions in mm
        const pdfWidth = 297;
        const pdfHeight = 210;

        // Calculate ratio to fit PDF page
        const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight);
        const finalWidth = imgWidth * ratio;
        const finalHeight = imgHeight * ratio;

        // Create PDF
        const pdf = new jsPDF({
            orientation,
            unit: 'mm',
            format,
        });

        // Add image to PDF (centered)
        const x = (pdfWidth - finalWidth) / 2;
        const y = (pdfHeight - finalHeight) / 2;

        pdf.addImage(
            canvas.toDataURL('image/jpeg', quality),
            'JPEG',
            x,
            y,
            finalWidth,
            finalHeight
        );

        return new Promise((resolve) => {
            pdf.getBlob((blob) => {
                resolve(blob);
            });
        });
    } catch (error) {
        console.error('PDF export failed:', error);
        throw new Error('PDF Export fehlgeschlagen: ' + error.message);
    }
}

/**
 * Download a blob as file
 * @param {Blob} blob - The blob to download
 * @param {string} filename - The filename
 * @param {string} mimeType - The MIME type
 */
export function downloadBlob(blob, filename, mimeType) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.type = mimeType;

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up
    setTimeout(() => URL.revokeObjectURL(url), 100);
}

/**
 * Export dashboard with filename based on current date
 * @param {HTMLElement} element - Dashboard element
 * @param {string} format - 'png' or 'pdf'
 * @param {string} dashboardName - Dashboard name for filename
 * @returns {Promise<void>}
 */
export async function exportDashboard(element, format, dashboardName = 'Dashboard') {
    const timestamp = new Date().toISOString().slice(0, 10);
    const sanitizedName = dashboardName.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    const filename = `${sanitizedName}_${timestamp}`;

    try {
        if (format === 'png') {
            const blob = await exportAsPNG(element);
            downloadBlob(blob, `${filename}.png`, 'image/png');
        } else if (format === 'pdf') {
            const blob = await exportAsPDF(element);
            downloadBlob(blob, `${filename}.pdf`, 'application/pdf');
        } else {
            throw new Error(`Unsupported format: ${format}`);
        }
    } catch (error) {
        console.error('Dashboard export failed:', error);
        throw error;
    }
}

/**
 * Export multiple charts as a grid
 * @param {Array<HTMLElement>} elements - Chart elements
 * @param {Object} options - Export options
 * @returns {Promise<Blob>} - PNG image blob
 */
export async function exportChartsGrid(elements, options = {}) {
    const {
        columns = 2,
        padding = 20,
        scale = 2,
    } = options;

    try {
        // Capture all charts
        const canvases = await Promise.all(
            elements.map((el) =>
                html2canvas(el, {
                    scale,
                    logging: false,
                    useCORS: true,
                    allowTaint: true,
                })
            )
        );

        // Calculate grid dimensions
        const rows = Math.ceil(elements.length / columns);
        const chartWidth = canvases[0].width;
        const chartHeight = canvases[0].height;

        const gridWidth = chartWidth * columns + padding * (columns + 1);
        const gridHeight = chartHeight * rows + padding * (rows + 1);

        // Create combined canvas
        const gridCanvas = document.createElement('canvas');
        gridCanvas.width = gridWidth;
        gridCanvas.height = gridHeight;
        const ctx = gridCanvas.getContext('2d');

        // White background
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, gridWidth, gridHeight);

        // Draw each chart in grid
        canvases.forEach((canvas, index) => {
            const col = index % columns;
            const row = Math.floor(index / columns);

            const x = padding + col * (chartWidth + padding);
            const y = padding + row * (chartHeight + padding);

            ctx.drawImage(canvas, x, y);
        });

        return new Promise((resolve) => {
            gridCanvas.toBlob((blob) => {
                resolve(blob);
            }, 'image/png');
        });
    } catch (error) {
        console.error('Grid export failed:', error);
        throw new Error('Grid Export fehlgeschlagen: ' + error.message);
    }
}

export default {
    exportAsPNG,
    exportAsPDF,
    exportDashboard,
    exportChartsGrid,
    downloadBlob,
};
