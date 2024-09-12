class CeleryWebSocketProgressBar extends CeleryProgressBar {
    constructor(progressUrl, options = {}) {
        super(progressUrl, options);
        this.websocketUrl = (location.protocol === 'https:' ? 'wss' : 'ws') + '://' + window.location.host + progressUrl;
    }

    connect() {
        const socket = new WebSocket(this.websocketUrl);

        socket.onopen = () => {
            socket.send(JSON.stringify({ 'type': 'check_task_completion' }));
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.complete) {
                if (data.success) {
                    this.onSuccess();
                } else {
                    this.onError();
                }
                socket.close();
            } else {
                this.onProgress(data.progress);
            }
        };

        socket.onerror = () => {
            this.onError();
        };
    }

    // A static method to simplify WebSocket progress bar initialization
    static initProgressBar(progressUrl, options) {
        const progressBar = new CeleryWebSocketProgressBar(progressUrl, options);
        progressBar.connect();
    }
}
