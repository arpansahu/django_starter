class CeleryProgressBar {
    constructor(progressUrl, options = {}) {
        this.progressUrl = progressUrl;
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

    // Handles the progress display
    onProgress(progress) {
        this.progressBarElement.style.width = progress.percent + "%";
        this.progressBarMessageElement.textContent = `${progress.current} of ${progress.total} processed.`;
    }

    // Updates on task success
    onSuccess() {
        this.progressBarElement.style.backgroundColor = this.barColors.success;
        this.progressBarMessageElement.textContent = "Task completed successfully!";
    }

    // Updates on task error
    onError() {
        this.progressBarElement.style.backgroundColor = this.barColors.error;
        this.progressBarMessageElement.textContent = "An error occurred during the task!";
    }

    async connect() {
        let response;
        try {
            response = await fetch(this.progressUrl);
        } catch (networkError) {
            this.onError();
            return;
        }

        if (response.ok) {
            const data = await response.json();
            if (data.complete) {
                this.onSuccess();
            } else {
                this.onProgress(data.progress);
                setTimeout(() => this.connect(), this.pollInterval);
            }
        } else {
            this.onError();
        }
    }

    // A static method to simplify progress bar initialization
    static initProgressBar(progressUrl, options) {
        const progressBar = new CeleryProgressBar(progressUrl, options);
        progressBar.connect();
    }
}
