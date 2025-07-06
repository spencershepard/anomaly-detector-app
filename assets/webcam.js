insertWebcam = () => {
    console.log("insertWebcam called");

    var container = document.getElementById("video-container");
    if (!container) {
        console.error("video-container element not found");
        return;
    }
    container.innerHTML = `
        <div class="video-wrapper">
            <video id="video" autoplay playsinline class="video-element"></video>
            <div id="action-overlay" class="action-overlay"></div>
        </div>
        <canvas id="canvas" width="640" height="480" class="canvas-hidden"></canvas>
    `;

    const video = document.getElementById("video");

    // Reusable overlay function
    const showOverlay = (message, overlayClass, duration = 1000) => {
        const overlay = document.getElementById("action-overlay");
        overlay.textContent = message;
        overlay.className = `action-overlay ${overlayClass}`;
        overlay.style.display = "flex";
        
        setTimeout(() => {
            overlay.style.display = "none";
        }, duration);
    };

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            console.log("Webcam stream started");
            video.srcObject = stream;
        })
        .catch(err => {
            console.error("Error accessing webcam:", err);
        });

    document.getElementById("capture-btn").addEventListener("click", () => {
        console.log("Capture button clicked");
        
        showOverlay("📸 Capturing...", "overlay-capture", 500);
        
        const canvas = document.getElementById("canvas");
        const ctx = canvas.getContext("2d");
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL("image/jpeg");
        console.log("Image captured from video, sending to server...");

        fetch("/capture-frame", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ image: imageData })
        })
        .then(res => {
            console.log("Received response from /upload-frame");
            return res.json();
        })
        .then(data => {
            console.log("Server response data:", data);
            document.getElementById("captured-image").src = imageData;
        })
        .catch(err => {
            console.error("Error during fetch/upload:", err);
        });
    });

    // Add validate button event listener
    document.getElementById("validate-btn").addEventListener("click", () => {
        console.log("Validate button clicked");
        showOverlay("✅ Validating...", "overlay-validate");
    });

    // Add classify button event listener
    document.getElementById("classify-btn").addEventListener("click", () => {
        console.log("Classify button clicked");
        showOverlay("🔍 Classifying...", "overlay-classify");
    });
};

window.addEventListener('DOMContentLoaded', () => {
    console.log("DOM fully loaded and parsed");
    // wait before initializing webcam
    setTimeout(insertWebcam, 2000);
});
