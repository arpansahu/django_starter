class CeleryWebSocketProgressBar extends CeleryProgressBar {

    constructor(progressUrl, options) {
        super(progressUrl, options);
    }

    async connect() {
        const ws = new WebSocket(`ws://${window.location.host}${this.progressUrl}`);
        ws.onopen = () => ws.send(JSON.stringify({'type': 'check_task_completion'}));

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.complete) {
                this.onSuccess();
                ws.close();
            } else {
                this.onProgress(data.progress);
            }
        };

        ws.onerror = () => {
            this.onError();
        };
    }
}
