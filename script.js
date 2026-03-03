// DOM Elements
const cookieInput = document.getElementById('cookie-input');
const loadFileBtn = document.getElementById('load-file-btn');
const pasteBtn = document.getElementById('paste-btn');
const clearBtn = document.getElementById('clear-btn');
const generateBtn = document.getElementById('generate-btn');
const progress = document.getElementById('progress');
const status = document.getElementById('status');
const results = document.getElementById('results');
const copyResultsBtn = document.getElementById('copy-results-btn');
const modeOptions = document.querySelectorAll('.mode-option');
const tabs = document.querySelectorAll('.tab');
const tabContents = document.querySelectorAll('.tab-content');
const batchFiles = document.getElementById('batch-files');
const fileList = document.getElementById('file-list');
const processBatchBtn = document.getElementById('process-batch-btn');
const batchProgress = document.getElementById('batch-progress');
const batchStatus = document.getElementById('batch-status');
const batchResults = document.getElementById('batch-results');
const saveResultsBtn = document.getElementById('save-results-btn');
const totalFiles = document.getElementById('total-files');
const validFiles = document.getElementById('valid-files');
const invalidFiles = document.getElementById('invalid-files');
const notification = document.getElementById('notification');

// Telegram Elements
const telegramToggle = document.getElementById('telegram-toggle');
const telegramConfig = document.getElementById('telegram-config');
const botTokenInput = document.getElementById('bot-token');
const chatIdInput = document.getElementById('chat-id');
const testTelegramBtn = document.getElementById('test-telegram-btn');
const telegramStatus = document.getElementById('telegram-status');

// Global variables
let currentMode = 'fullinfo';
let selectedFiles = [];
let batchResultsData = [];

// --- BẮT ĐẦU PHẦN ĐA NGÔN NGỮ ---
const i18n = {
    vi: {
        // Tiêu đề ứng dụng - KHÔNG thay đổi "Netflix Cookies Checker"
        tagline: "ZALO : 0353099675 - WEB:CAMEYOU.SHOP",
        apiDocs: "Tài liệu API",

        // Tabs
        tabSingle: "Nhập Đơn",
        tabBatch: "Xử Lý Hàng Loạt",
        tabAbout: "Giới Thiệu",

        // Card: Nhập Cookie
        cardCookieTitle: "Nhập Cookie",
        cookieLabel: "Dán cookie Netflix của bạn vào đây:",
        cookiePlaceholder: "Dán cookie theo định dạng JSON, text hoặc Netscape...",
        btnLoadFile: "Tải từ File",
        btnPaste: "Dán Clipboard",
        btnClear: "Xóa",
        modeFullInfo: "Thông Tin Đầy Đủ",
        modeTokenOnly: "Chỉ Token",
        btnGenerate: "Tạo Token",
        statusReady: "Sẵn sàng",

        // Card: Telegram
        cardTelegramTitle: "Gửi Kết Quả Telegram",
        telegramToggleLabel: "Bật gửi Telegram",
        telegramBotToken: "Bot Token:",
        telegramChatId: "Chat ID:",
        btnTestTelegram: "Kiểm Tra Kết Nối",
        telegramDisabled: "Telegram đang tắt",
        telegramEnabled: "Telegram đang bật",
        telegramTesting: "Đang kiểm tra kết nối Telegram...",
        telegramSuccess: "Kết nối Telegram thành công!",
        telegramFailed: "Kết nối Telegram thất bại",

        // Card: Kết Quả
        cardResultsTitle: "Kết Quả",
        noResultsTitle: "Chưa có kết quả",
        noResultsContent: "Hãy xử lý cookie để xem kết quả tại đây.",
        btnCopyResults: "Sao Chép Kết Quả",

        // Card: Batch Processing
        cardBatchTitle: "Xử Lý Hàng Loạt",
        batchFileLabel: "Chọn nhiều file cookie:",
        noFilesSelected: "Chưa chọn file nào",
        btnProcessBatch: "Xử Lý Tất Cả",
        batchStatusReady: "Sẵn sàng",

        // Card: Batch Results
        cardBatchResultsTitle: "Kết Quả Hàng Loạt",
        batchSummaryTitle: "Tổng Kết Xử Lý",
        statTotalFiles: "Tổng File",
        statValidFiles: "Hợp Lệ",
        statInvalidFiles: "Không Hợp Lệ",
        noResultsYet: "Chưa có kết quả",
        btnSaveResults: "Lưu Kết Quả",

        // About tab
        aboutTitle: "Giới Thiệu Netflix Cookies Checker",
        aboutDesc1: "Ứng dụng này trích xuất <strong>NetflixId</strong> từ nhiều định dạng cookie khác nhau và tạo ra link đăng nhập trực tiếp vào tài khoản Netflix.",
        aboutDesc2: "Web này check cookie và gen link login app Netflix qua link",
        featuresTitle: "Tính Năng:",
        feature1: "Trích xuất NetflixId từ file text, JSON hoặc cookie",
        feature2: "Kiểm tra tính hợp lệ và thông tin tài khoản",
        feature3: "Tạo token đăng nhập trực tiếp",
        feature4: "Xử lý hàng loạt nhiều file cùng lúc",
        feature5: "Gửi kết quả hợp lệ qua Telegram",
        formatsTitle: "Định Dạng Hỗ Trợ:",
        format1: "File text chứa cookie",
        format2: "File JSON chứa cookie",
        format3: "File ZIP chứa nhiều file cookie",
        format4: "Chuỗi header có cookie NetflixId",
        format5: "File cookie định dạng Netscape",
        telegramSetupTitle: "Cài Đặt Telegram:",
        telegramStep1: "Tạo bot với @BotFather trên Telegram",
        telegramStep2: "Lấy token bot từ BotFather",
        telegramStep3: "Mở chat với bot và gửi bất kỳ tin nhắn nào",
        telegramStep4: "Lấy Chat ID tại: https://api.telegram.org/bot&lt;YourBOTToken&gt;/getUpdates",
        telegramStep5: "Bật tính năng gửi Telegram và nhập thông tin xác thực",
        usageTitle: "Hướng Dẫn Sử Dụng:",
        usageStep1: "Dán cookie hoặc tải từ file ở tab <strong>Nhập Đơn</strong>",
        usageStep2: "Cấu hình gửi Telegram nếu muốn (tùy chọn)",
        usageStep3: "Chọn chế độ xuất dữ liệu (Thông Tin Đầy Đủ hoặc Chỉ Token)",
        usageStep4: "Nhấn <strong>\"Tạo Token\"</strong> để xử lý",
        usageStep5: "Để xử lý nhiều file, dùng tab <strong>Xử Lý Hàng Loạt</strong>",
        aboutNote: "<strong>Lưu ý:</strong> Công cụ này chỉ dành cho mục đích học tập và nghiên cứu.",

        // Footer
        footerText: "CAMEYOU - TPTTH",
        footerYtb: "CAMEYOU.SHOP",

        // Notification messages
        notifFileLoaded: "Tải file thành công",
        notifPasted: "Đã dán nội dung từ clipboard",
        notifCleared: "Đã xóa nội dung",
        notifNoContent: "Vui lòng nhập nội dung trước",
        notifClipboardFail: "Không đọc được clipboard",
        notifTokenSuccess: "Tạo token thành công",
        notifCopied: "Đã sao chép vào clipboard",
        notifCopyFail: "Sao chép thất bại",
        notifSelectFiles: "Vui lòng chọn file trước",
        notifNoSave: "Không có kết quả để lưu",
        notifSaved: "Đã lưu kết quả thành công",
        notifTelegramSaved: "Đã lưu cấu hình Telegram",
        notifTelegramError: "Lỗi lưu cấu hình Telegram",
        notifTelegramSuccess: "Kiểm tra Telegram thành công!",
        notifNeedBothFields: "Vui lòng nhập cả Bot Token và Chat ID",

        // Dynamic JS text
        accOverview: "TỔNG QUAN TÀI KHOẢN",
        accInfo: "THÔNG TIN TÀI KHOẢN",
        tokenInfo: "THÔNG TIN TOKEN",
        valid: "Hoạt động",
        invalid: "Lỗi",
        yes: "Có",
        no: "Không",
        genFail: "TẠO TOKEN THẤT BẠI",
        copyLogin: "Sao chép Link Đăng nhập",
        copyToken: "Sao chép Token",
        timeRemain: "Thời gian còn lại",
        processing: "Đang xử lý...",
        batchProcessing: "Đang xử lý hàng loạt...",
        batchComplete: "Xử lý hoàn tất",
        batchFailed: "Xử lý thất bại",
        processComplete: "Xử lý hoàn tất",
        processFailed: "Xử lý thất bại",
        pending: "Chờ xử lý",
        filePending: "Chờ xử lý",
        fileProcessing: "Đang xử lý..."
    },
    en: {
        // App title - NEVER change "Netflix Cookies Checker"
        tagline: "ZALO : 0353099675 - WEB:CAMEYOU.SHOP",
        apiDocs: "API Docs",

        // Tabs
        tabSingle: "Single Input",
        tabBatch: "Batch Processing",
        tabAbout: "About",

        // Card: Input Cookies
        cardCookieTitle: "Input Cookies",
        cookieLabel: "Paste your Netflix cookies here:",
        cookiePlaceholder: "Paste cookies in JSON format, text format, or Netscape format...",
        btnLoadFile: "Load from File",
        btnPaste: "Paste from Clipboard",
        btnClear: "Clear",
        modeFullInfo: "Full Info",
        modeTokenOnly: "Token Only",
        btnGenerate: "Generate Token",
        statusReady: "Ready",

        // Card: Telegram
        cardTelegramTitle: "Telegram Hit Sender",
        telegramToggleLabel: "Enable Telegram Hits",
        telegramBotToken: "Bot Token:",
        telegramChatId: "Chat ID:",
        btnTestTelegram: "Test Connection",
        telegramDisabled: "Telegram hits are disabled",
        telegramEnabled: "Telegram hits are enabled",
        telegramTesting: "Testing Telegram connection...",
        telegramSuccess: "Telegram connection successful!",
        telegramFailed: "Telegram connection failed",

        // Card: Results
        cardResultsTitle: "Results",
        noResultsTitle: "No results yet",
        noResultsContent: "Process some cookies to see results here.",
        btnCopyResults: "Copy Results",

        // Card: Batch Processing
        cardBatchTitle: "Batch Processing",
        batchFileLabel: "Select multiple cookie files:",
        noFilesSelected: "No files selected",
        btnProcessBatch: "Process Batch",
        batchStatusReady: "Ready",

        // Card: Batch Results
        cardBatchResultsTitle: "Batch Results",
        batchSummaryTitle: "Processing Summary",
        statTotalFiles: "Total Files",
        statValidFiles: "Valid",
        statInvalidFiles: "Invalid",
        noResultsYet: "No results yet",
        btnSaveResults: "Save Results",

        // About tab
        aboutTitle: "About Netflix Cookies Checker",
        aboutDesc1: "This application extracts <strong>NetflixId</strong> from various cookie formats and generates direct login tokens.",
        aboutDesc2: "This web tool checks cookies and generates Netflix login links.",
        featuresTitle: "Features:",
        feature1: "Extract NetflixId from text, JSON, or cookie files",
        feature2: "Check account validity and details",
        feature3: "Generate direct login tokens",
        feature4: "Batch processing of multiple files",
        feature5: "Telegram hit sender for valid accounts",
        formatsTitle: "Supported Formats:",
        format1: "Text files with cookies",
        format2: "JSON files with cookies",
        format3: "ZIP files containing multiple cookie files",
        format4: "Header strings with NetflixId cookie",
        format5: "Netscape format cookie files",
        telegramSetupTitle: "Telegram Setup:",
        telegramStep1: "Create a bot with @BotFather on Telegram",
        telegramStep2: "Get your bot token from BotFather",
        telegramStep3: "Start a chat with your bot and send any message",
        telegramStep4: "Get your chat ID from: https://api.telegram.org/bot&lt;YourBOTToken&gt;/getUpdates",
        telegramStep5: "Enable Telegram hits and enter your credentials",
        usageTitle: "Usage:",
        usageStep1: "Paste cookies or load from file in the <strong>Single Input</strong> tab",
        usageStep2: "Configure Telegram hits if desired (optional)",
        usageStep3: "Select your preferred output mode (Full Info or Token Only)",
        usageStep4: "Click <strong>\"Generate Token\"</strong> to process",
        usageStep5: "For multiple files, use the <strong>Batch Processing</strong> tab",
        aboutNote: "<strong>Note:</strong> This tool is for educational purposes only.",

        // Footer
        footerText: "TPTTH CAMEYOUSHOP &copy; 2025",
        footerYtb: "",

        // Notification messages
        notifFileLoaded: "File loaded successfully",
        notifPasted: "Content pasted from clipboard",
        notifCleared: "Input cleared",
        notifNoContent: "Please enter some content first",
        notifClipboardFail: "Failed to read clipboard",
        notifTokenSuccess: "Token generated successfully",
        notifCopied: "Copied to clipboard",
        notifCopyFail: "Failed to copy",
        notifSelectFiles: "Please select files first",
        notifNoSave: "No results to save",
        notifSaved: "Results saved successfully",
        notifTelegramSaved: "Telegram configuration saved",
        notifTelegramError: "Error saving Telegram config",
        notifTelegramSuccess: "Telegram test successful!",
        notifNeedBothFields: "Please enter both Bot Token and Chat ID",

        // Dynamic JS text
        accOverview: "ACCOUNT OVERVIEW",
        accInfo: "ACCOUNT INFORMATION",
        tokenInfo: "TOKEN INFORMATION",
        valid: "Valid",
        invalid: "Invalid",
        yes: "Yes",
        no: "No",
        genFail: "TOKEN GENERATION FAILED",
        copyLogin: "Copy Login URL",
        copyToken: "Copy Token",
        timeRemain: "Time Remaining",
        processing: "Processing...",
        batchProcessing: "Processing batch...",
        batchComplete: "Batch processing complete",
        batchFailed: "Batch processing failed",
        processComplete: "Processing complete",
        processFailed: "Processing failed",
        pending: "Pending",
        filePending: "Pending",
        fileProcessing: "Processing..."
    }
};

let currentAppLang = 'vi'; // Mặc định là tiếng Việt

function changeLanguage(lang) {
    currentAppLang = lang;
    const t = i18n[lang];

    // Đổi trạng thái nút ngôn ngữ
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });

    // === Dịch các phần tử có data-i18n (text content) ===
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key] !== undefined) {
            el.innerHTML = t[key];
        }
    });

    // === Dịch placeholder có data-i18n-placeholder ===
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (t[key] !== undefined) {
            el.placeholder = t[key];
        }
    });

    // === Dịch aria-label có data-i18n-aria ===
    document.querySelectorAll('[data-i18n-aria]').forEach(el => {
        const key = el.getAttribute('data-i18n-aria');
        if (t[key] !== undefined) {
            el.setAttribute('aria-label', t[key]);
        }
    });
}

function initLanguageSwitch() {
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            changeLanguage(e.target.dataset.lang);
        });
    });
    changeLanguage('vi'); // Khởi tạo mặc định là tiếng Việt
}
// --- KẾT THÚC PHẦN ĐA NGÔN NGỮ ---

// Event Listeners
document.addEventListener('DOMContentLoaded', initApp);
loadFileBtn.addEventListener('click', handleLoadFile);
pasteBtn.addEventListener('click', handlePaste);
clearBtn.addEventListener('click', handleClear);
generateBtn.addEventListener('click', handleGenerate);
copyResultsBtn.addEventListener('click', handleCopyResults);
modeOptions.forEach(option => {
    option.addEventListener('click', handleModeChange);
});
tabs.forEach(tab => {
    tab.addEventListener('click', handleTabChange);
});
batchFiles.addEventListener('change', handleBatchFilesChange);
processBatchBtn.addEventListener('click', handleProcessBatch);
saveResultsBtn.addEventListener('click', handleSaveResults);

// Initialize the application
function initApp() {
    updateFileList();
    initTelegram();
    handleResponsive();
    initLanguageSwitch(); // Gọi khởi tạo ngôn ngữ ở đây

    // Add resize listener
    window.addEventListener('resize', handleResponsive);
}

// Handle responsive behavior
function handleResponsive() {
    const width = window.innerWidth;

    if (width < 768) {
        // Mobile optimizations
        document.body.classList.add('mobile');

        // Adjust card padding for mobile
        document.querySelectorAll('.card').forEach(card => {
            card.style.padding = '15px';
        });

    } else {
        document.body.classList.remove('mobile');

        // Reset card padding for desktop
        document.querySelectorAll('.card').forEach(card => {
            card.style.padding = '25px';
        });
    }
}

// Handle mode change (Full Info / Token Only)
function handleModeChange(e) {
    const mode = e.target.dataset.mode;
    currentMode = mode;

    modeOptions.forEach(option => {
        option.classList.remove('active');
    });

    e.target.classList.add('active');
}

// Handle tab change
function handleTabChange(e) {
    const tabId = e.target.dataset.tab;

    tabs.forEach(tab => {
        tab.classList.remove('active');
    });

    tabContents.forEach(content => {
        content.classList.remove('active');
    });

    e.target.classList.add('active');
    document.getElementById(`${tabId}-tab`).classList.add('active');
}

// Handle load file
function handleLoadFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.txt,.json,.zip';

    input.onchange = e => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = e => {
            cookieInput.value = e.target.result;
            showNotification(i18n[currentAppLang].notifFileLoaded);
        };
        reader.readAsText(file);
    };

    input.click();
}

// Handle paste from clipboard
function handlePaste() {
    navigator.clipboard.readText()
        .then(text => {
            cookieInput.value = text;
            showNotification(i18n[currentAppLang].notifPasted);
        })
        .catch(err => {
            showNotification(i18n[currentAppLang].notifClipboardFail, true);
        });
}

// Handle clear input
function handleClear() {
    cookieInput.value = '';
    showNotification(i18n[currentAppLang].notifCleared);
}

// Handle generate token
async function handleGenerate() {
    const content = cookieInput.value.trim();
    if (!content) {
        showNotification(i18n[currentAppLang].notifNoContent, true);
        return;
    }

    // Disable button and show progress
    generateBtn.disabled = true;
    generateBtn.innerHTML = `<div class="spinner"></div> ${i18n[currentAppLang].processing}`;
    progress.style.width = '0%';
    status.textContent = i18n[currentAppLang].processing;

    try {
        const response = await fetch('/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                mode: currentMode
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            progress.style.width = '100%';
            status.textContent = i18n[currentAppLang].processComplete;
            displayResults(data);
            showNotification(i18n[currentAppLang].notifTokenSuccess);
        } else {
            progress.style.width = '100%';
            status.textContent = i18n[currentAppLang].processFailed;
            displayError(data.message);
            showNotification(data.message, true);
        }
    } catch (error) {
        progress.style.width = '100%';
        status.textContent = i18n[currentAppLang].processFailed;
        displayError('Network error: ' + error.message);
        showNotification('Network error: ' + error.message, true);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = `<i class="fas fa-key"></i> ${i18n[currentAppLang].btnGenerate}`;
    }
}

// Handle copy results
function handleCopyResults() {
    const resultsText = results.innerText;
    navigator.clipboard.writeText(resultsText)
        .then(() => {
            showNotification(i18n[currentAppLang].notifCopied);
        })
        .catch(err => {
            showNotification(i18n[currentAppLang].notifCopyFail, true);
        });
}

// Handle batch files change
function handleBatchFilesChange(e) {
    selectedFiles = Array.from(e.target.files);
    updateFileList();
}

// Update file list display
function updateFileList() {
    fileList.innerHTML = '';

    if (selectedFiles.length === 0) {
        fileList.innerHTML = `<div class="file-item"><span>${i18n[currentAppLang].noFilesSelected}</span></div>`;
        return;
    }

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span>${file.name}</span>
            <span class="file-status">${i18n[currentAppLang].filePending}</span>
        `;
        fileList.appendChild(fileItem);
    });

    totalFiles.textContent = selectedFiles.length;
    validFiles.textContent = '0';
    invalidFiles.textContent = '0';
}

// Update file list to show processing status
function updateFileListProcessing() {
    fileList.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        fileItem.innerHTML = `
            <span>${file.name}</span>
            <span class="file-status processing">${i18n[currentAppLang].fileProcessing}</span>
        `;
        fileList.appendChild(fileItem);
    });
}

// Handle process batch
async function handleProcessBatch() {
    if (selectedFiles.length === 0) {
        showNotification(i18n[currentAppLang].notifSelectFiles, true);
        return;
    }

    // Reset results
    batchResultsData = [];
    batchResults.innerHTML = '';
    saveResultsBtn.disabled = true;

    // Disable button and show progress
    processBatchBtn.disabled = true;
    processBatchBtn.innerHTML = `<div class="spinner"></div> ${i18n[currentAppLang].processing}`;
    batchProgress.style.width = '0%';
    batchStatus.textContent = i18n[currentAppLang].batchProcessing;

    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });
    formData.append('mode', currentMode);

    try {
        // Update file list status to processing
        updateFileListProcessing();

        const response = await fetch('/api/batch-check', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            batchResultsData = data.results;
            displayBatchResults(batchResultsData);
            batchProgress.style.width = '100%';
            batchStatus.textContent = i18n[currentAppLang].batchComplete;
            saveResultsBtn.disabled = false;
            showNotification(`${i18n[currentAppLang].batchComplete}: ${batchResultsData.filter(r => r.status === 'success').length} ${i18n[currentAppLang].statValidFiles}, ${batchResultsData.filter(r => r.status === 'error').length} ${i18n[currentAppLang].statInvalidFiles}`);
        } else {
            batchProgress.style.width = '100%';
            batchStatus.textContent = i18n[currentAppLang].batchFailed;
            showNotification(data.message, true);
        }
    } catch (error) {
        batchProgress.style.width = '100%';
        batchStatus.textContent = i18n[currentAppLang].batchFailed;
        showNotification('Network error: ' + error.message, true);
    } finally {
        processBatchBtn.disabled = false;
        processBatchBtn.innerHTML = `<i class="fas fa-cogs"></i> ${i18n[currentAppLang].btnProcessBatch}`;
    }
}

// Display batch results in detailed single line format
function displayBatchResults(results) {
    batchResults.innerHTML = '';

    let validCount = 0;
    let invalidCount = 0;

    results.forEach(result => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item single-line-result';

        if (result.status === 'success') {
            const account = result.account_info;
            const token = result.token_result;

            let statusText = `✅ ${result.filename} | `;
            statusText += `Status: ${account.ok ? 'Valid' : 'Invalid'} | `;
            statusText += `Premium: ${account.premium ? 'Yes' : 'No'} | `;
            statusText += `Country: ${account.country} | `;
            statusText += `Plan: ${account.plan} | `;
            statusText += `Price: ${account.plan_price} | `;
            statusText += `Payment Hold: ${account.on_payment_hold} | `;
            statusText += `Max Streams: ${account.max_streams}`;

            if (token.status === 'Success') {
                statusText += ` | Token: ${token.token.substring(0, 15)}...`;
            }

            fileItem.innerHTML = `
                <div class="file-info">
                    <span>${statusText}</span>
                </div>
                <span class="file-status valid">Valid</span>
            `;
            validCount++;
        } else {
            fileItem.innerHTML = `
                <div class="file-info">
                    <span>❌ ${result.filename}: ${result.message}</span>
                </div>
                <span class="file-status invalid">Invalid</span>
            `;
            invalidCount++;
        }

        batchResults.appendChild(fileItem);
    });

    validFiles.textContent = validCount;
    invalidFiles.textContent = invalidCount;

    // Update success rate
    const successRate = ((validCount / results.length) * 100).toFixed(2);
    batchStatus.textContent = `Complete - Success Rate: ${successRate}%`;
}

// Handle save results
function handleSaveResults() {
    if (batchResultsData.length === 0) {
        showNotification(i18n[currentAppLang].notifNoSave, true);
        return;
    }

    let content = 'Netflix Cookies Checker - Batch Results\n';
    content += 'Generated on: ' + new Date().toLocaleString() + '\n';
    content += 'Created by: t.me/still_alivenow (Ichigo Kurosaki)\n\n';
    content += '='.repeat(80) + '\n\n';

    let validCount = 0;
    let invalidCount = 0;

    batchResultsData.forEach(result => {
        if (result.status === 'success') {
            validCount++;
            const account = result.account_info;
            const token = result.token_result;

            content += `✅ ${result.filename}\n`;
            content += `NetflixId: ${result.netflix_id}\n`;
            content += `Status: ${account.ok ? 'Valid' : 'Invalid'}\n`;
            content += `Premium: ${account.premium ? 'Yes' : 'No'}\n`;
            content += `Country: ${account.country}\n`;
            content += `Plan: ${account.plan}\n`;
            content += `Price: ${account.plan_price}\n`;
            content += `Member Since: ${account.member_since}\n`;
            content += `Payment Method: ${account.payment_method}\n`;
            content += `Phone: ${account.phone}\n`;
            content += `Phone Verified: ${account.phone_verified}\n`;
            content += `Video Quality: ${account.video_quality}\n`;
            content += `Max Streams: ${account.max_streams}\n`;
            content += `Payment Hold: ${account.on_payment_hold}\n`;
            content += `Extra Member: ${account.extra_member}\n`;
            content += `Email: ${account.email}\n`;
            content += `Email Verified: ${account.email_verified}\n`;
            content += `Profiles: ${account.profiles}\n`;
            content += `Billing: ${account.next_billing}\n`;

            if (token.status === 'Success') {
                content += `Token: ${token.token}\n`;
                content += `Login URL: ${token.direct_login_url}\n`;
                content += `Token Expires: ${new Date(token.expires * 1000).toLocaleString()}\n`;
                content += `Time Remaining: ${Math.floor(token.time_remaining / 86400)}d ${Math.floor((token.time_remaining % 86400) / 3600)}h ${Math.floor((token.time_remaining % 3600) / 60)}m\n`;
            } else {
                content += `Token Error: ${token.error}\n`;
            }

            content += '\n' + '─'.repeat(80) + '\n\n';
        } else {
            invalidCount++;
            content += `❌ ${result.filename}: ${result.message}\n\n`;
            content += '─'.repeat(80) + '\n\n';
        }
    });

    content += `\nSUMMARY\n`;
    content += `Total Files: ${batchResultsData.length}\n`;
    content += `Valid: ${validCount}\n`;
    content += `Invalid: ${invalidCount}\n`;
    content += `Success Rate: ${((validCount / batchResultsData.length) * 100).toFixed(2)}%\n`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `netflix_batch_results_${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showNotification(i18n[currentAppLang].notifSaved);
}

// Enhanced displayResults function with large display and language support
function displayResults(data) {
    let html = '';
    const t = i18n[currentAppLang]; // Lấy từ điển hiện tại

    if (currentMode === 'fullinfo') {
        const account = data.account_info;
        const statusText = account.ok ? t.valid : t.invalid;
        const premiumText = account.premium ? t.yes : t.no;

        html = `
            <div class="result-item">
                <div class="result-title" style="font-size: 1.2rem; padding-bottom: 10px; border-bottom: 1px solid var(--dark-light);">
                    <i class="fas fa-user-circle"></i>
                    ${t.accOverview}
                    ${data.telegram_sent ? '<span class="telegram-hit-indicator"><i class="fab fa-telegram"></i> Telegram</span>' : ''}
                </div>
                <div class="result-content" style="margin-top: 15px;">
                    <div class="quick-stats">
                        <div class="stat-badge ${account.ok ? 'valid' : 'invalid'}" style="font-size: 1rem; padding: 8px 15px;">${statusText.toUpperCase()}</div>
                        <div class="stat-badge ${account.premium ? 'premium' : 'basic'}" style="font-size: 1rem; padding: 8px 15px;">${account.premium ? 'PREMIUM' : 'BASIC'}</div>
                        <div class="stat-badge country" style="font-size: 1rem; padding: 8px 15px;">${account.country}</div>
                    </div>
                    
                    <div class="dropdown-content">
                        <div class="section-header">
                            <i class="fas fa-id-card"></i>
                            ${t.accInfo}
                        </div>
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="info-label">Status:</span>
                                <span class="info-value ${account.ok ? 'status-valid' : 'status-invalid'}">${statusText}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Premium:</span>
                                <span class="info-value ${account.premium ? 'status-premium' : ''}">${premiumText}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Country:</span>
                                <span class="info-value">${account.country}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Plan:</span>
                                <span class="info-value">${account.plan}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Price:</span>
                                <span class="info-value">${account.plan_price}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Member Since:</span>
                                <span class="info-value">${account.member_since}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Payment Method:</span>
                                <span class="info-value">${account.payment_method}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Phone:</span>
                                <span class="info-value">${account.phone}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Phone Verified:</span>
                                <span class="info-value">${account.phone_verified}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Video Quality:</span>
                                <span class="info-value">${account.video_quality}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Max Streams:</span>
                                <span class="info-value">${account.max_streams}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Payment Hold:</span>
                                <span class="info-value">${account.on_payment_hold}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Extra Member:</span>
                                <span class="info-value">${account.extra_member}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Email:</span>
                                <span class="info-value">${account.email.replace(/\\x40/g, '@')}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Email Verified:</span>
                                <span class="info-value">${account.email_verified}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Profiles:</span>
                                <span class="info-value">${account.profiles}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Billing:</span>
                                <span class="info-value">${account.next_billing}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    const token = data.token_result;
    if (token.status === 'Success') {
        const genTime = new Date(token.generation_time * 1000).toLocaleString();
        const expTime = new Date(token.expires * 1000).toLocaleString();

        const days = Math.floor(token.time_remaining / 86400);
        const hours = Math.floor((token.time_remaining % 86400) / 3600);
        const minutes = Math.floor((token.time_remaining % 3600) / 60);
        const seconds = token.time_remaining % 60;

        html += `
            <div class="result-item">
                <div class="result-title" style="font-size: 1.2rem;">
                    <i class="fas fa-key"></i>
                    ${t.tokenInfo}
                </div>
                <div class="result-content">
                    <div class="token-info" style="padding: 20px;">
                        <div class="info-grid">
                            <div class="info-item">
                                <span class="info-label">Status:</span>
                                <span class="info-value status-valid">${token.status}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Generation Time:</span>
                                <span class="info-value">${genTime}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">Expiry:</span>
                                <span class="info-value">${expTime}</span>
                            </div>
                            <div class="info-item">
                                <span class="info-label">${t.timeRemain}:</span>
                                <span class="info-value">${days}d ${hours}h ${minutes}m ${seconds}s</span>
                            </div>
                        </div>
                        
                        <div style="margin-top: 20px;">
                            <div class="info-label" style="margin-bottom: 8px; font-size: 1rem;">Direct Login URL:</div>
                            <div class="token-url" style="font-size: 0.9rem; padding: 15px;">${token.direct_login_url}</div>
                            <button class="copy-btn" data-text="${token.direct_login_url}" style="padding: 10px 20px; font-size: 1rem;">
                                <i class="fas fa-copy"></i> ${t.copyLogin}
                            </button>
                        </div>
                        
                        <div style="margin-top: 20px;">
                            <div class="info-label" style="margin-bottom: 8px; font-size: 1rem;">Token:</div>
                            <div class="token-url" style="font-size: 0.9rem; padding: 15px;">${token.token}</div>
                            <button class="copy-btn" data-text="${token.token}" style="padding: 10px 20px; font-size: 1rem;">
                                <i class="fas fa-copy"></i> ${t.copyToken}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } else {
        html += `
            <div class="result-item">
                <div class="result-title" style="font-size: 1.2rem;">
                    <i class="fas fa-times-circle" style="color: var(--danger);"></i>
                    ${t.genFail}
                </div>
                <div class="result-content">
                    <div class="info-item">
                        <span class="info-label">Error:</span>
                        <span class="info-value">${token.error}</span>
                    </div>
                </div>
            </div>
        `;
    }

    // Update the results container
    results.innerHTML = html;

    // Enable copy buttons
    copyResultsBtn.disabled = false;

    // Add event listeners to copy buttons
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const text = this.dataset.text;
            navigator.clipboard.writeText(text)
                .then(() => {
                    showNotification(i18n[currentAppLang].notifCopied);
                })
                .catch(err => {
                    showNotification(i18n[currentAppLang].notifCopyFail, true);
                });
        });
    });
}

// Display error
function displayError(message) {
    results.innerHTML = `
        <div class="result-item">
            <div class="result-title">
                <i class="fas fa-times-circle" style="color: var(--danger);"></i>
                Error
            </div>
            <div class="result-content">
                ${message}
            </div>
        </div>
    `;
    copyResultsBtn.disabled = false;
}

// Show notification
function showNotification(message, isError = false) {
    notification.textContent = message;
    notification.className = 'notification';

    if (isError) {
        notification.classList.add('error');
    }

    notification.classList.add('show');

    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// Telegram Hit Sender functionality

// Load saved Telegram config
function loadTelegramConfig() {
    const savedConfig = localStorage.getItem('telegramConfig');
    if (savedConfig) {
        const config = JSON.parse(savedConfig);
        telegramToggle.checked = config.enabled || false;
        botTokenInput.value = config.bot_token || '';
        chatIdInput.value = config.chat_id || '';
        updateTelegramUI();
    }
}

// Update Telegram UI based on toggle state
function updateTelegramUI() {
    const t = i18n[currentAppLang];
    if (telegramToggle.checked) {
        telegramConfig.style.display = 'block';
        telegramStatus.className = 'telegram-status enabled';
        telegramStatus.innerHTML = `<i class="fas fa-check-circle"></i> ${t.telegramEnabled}`;
    } else {
        telegramConfig.style.display = 'none';
        telegramStatus.className = 'telegram-status disabled';
        telegramStatus.innerHTML = `<i class="fas fa-times-circle"></i> ${t.telegramDisabled}`;
    }
}

// Save Telegram config
function saveTelegramConfig() {
    const config = {
        enabled: telegramToggle.checked,
        bot_token: botTokenInput.value,
        chat_id: chatIdInput.value
    };
    localStorage.setItem('telegramConfig', JSON.stringify(config));

    // Send to server
    fetch('/api/telegram-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                showNotification(i18n[currentAppLang].notifTelegramSaved);
            } else {
                showNotification(i18n[currentAppLang].notifTelegramError, true);
            }
        })
        .catch(error => {
            showNotification(i18n[currentAppLang].notifTelegramError, true);
        });
}

// Test Telegram connection
function testTelegramConnection() {
    if (!botTokenInput.value || !chatIdInput.value) {
        showNotification(i18n[currentAppLang].notifNeedBothFields, true);
        return;
    }

    const t = i18n[currentAppLang];
    testTelegramBtn.disabled = true;
    testTelegramBtn.innerHTML = `<div class="spinner"></div> ${t.processing}`;
    telegramStatus.className = 'telegram-status testing';
    telegramStatus.innerHTML = `<i class="fas fa-sync-alt"></i> ${t.telegramTesting}`;

    // Simple test by sending a test message
    const testMessage = {
        chat_id: chatIdInput.value,
        text: '✅ Netflix Cookies Checker Test\n\nThis is a test message from your Netflix Cookies Checker. If you receive this, your Telegram configuration is working correctly!',
        parse_mode: 'Markdown'
    };

    fetch(`https://api.telegram.org/bot${botTokenInput.value}/sendMessage`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(testMessage)
    })
        .then(response => response.json())
        .then(data => {
            const t2 = i18n[currentAppLang];
            if (data.ok) {
                telegramStatus.className = 'telegram-status enabled';
                telegramStatus.innerHTML = `<i class="fas fa-check-circle"></i> ${t2.telegramSuccess}`;
                showNotification(t2.notifTelegramSuccess);
            } else {
                telegramStatus.className = 'telegram-status disabled';
                telegramStatus.innerHTML = `<i class="fas fa-times-circle"></i> ${t2.telegramFailed}: ${data.description || 'Unknown error'}`;
                showNotification(t2.telegramFailed + ': ' + (data.description || 'Unknown error'), true);
            }
        })
        .catch(error => {
            const t2 = i18n[currentAppLang];
            telegramStatus.className = 'telegram-status disabled';
            telegramStatus.innerHTML = `<i class="fas fa-times-circle"></i> ${t2.telegramFailed}`;
            showNotification(t2.telegramFailed, true);
        })
        .finally(() => {
            testTelegramBtn.disabled = false;
            testTelegramBtn.innerHTML = `<i class="fas fa-paper-plane"></i> ${i18n[currentAppLang].btnTestTelegram}`;
        });
}

// Initialize Telegram functionality
function initTelegram() {
    loadTelegramConfig();

    telegramToggle.addEventListener('change', function () {
        updateTelegramUI();
        saveTelegramConfig();
    });

    botTokenInput.addEventListener('input', saveTelegramConfig);
    chatIdInput.addEventListener('input', saveTelegramConfig);
    testTelegramBtn.addEventListener('click', testTelegramConnection);

    updateTelegramUI();
}