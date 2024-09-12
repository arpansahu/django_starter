class CeleryProgressBar {

    constructor(progressUrl, options) {
        this.progressUrl = progressUrl;
        options = options || {};
        this.progressBarElement = options.progressBarElement || document.getElementById('progress-bar');
        this.progressBarMessageElement = options.progressBarMessageElement || document.getElementById('progress-bar-message');
        this.pollInterval = options.pollInterval || 500;
        this.barColors = Object.assign({
            success: '#76ce60',
            error: '#dc4f63',
            progress: '#68a9ef',
        }, options.barColors);
        this.messages = Object.assign({
            waiting: 'Waiting for task to start...',
            started: 'Task started...',
        }, options.messages);
    }

    onProgress(progress) {
        this.progressBarElement.style.width = progress.percent + "%";
        if (progress.current === 0) {
            this.progressBarMessageElement.textContent = this.messages.waiting;
        } else {
            this.progressBarMessageElement.textContent = `${progress.current} of ${progress.total} processed.`;
        }
    }

    onSuccess() {
        this.progressBarElement.style.backgroundColor = this.barColors.success;
    }

    onError() {
        this.progressBarElement.style.backgroundColor = this.barColors.error;
    }

    async connect() {
        const response = await fetch(this.progressUrl);
        const data = await response.json();
        if (data.complete) {
            this.onSuccess();
        } else {
            this.onProgress(data.progress);
            setTimeout(() => this.connect(), this.pollInterval);
        }
    }
}
