// Streamlit Component Library
window.Streamlit = {
    RENDER_EVENT: "streamlit:render",
    events: {
        addEventListener: function(type, callback) {
            window.addEventListener("message", function(event) {
                if (event.data.type === type) {
                    callback(event.data);
                }
            });
        }
    },
    setComponentReady: function() {
        window.parent.postMessage({ type: "streamlit:componentReady", height: window.innerHeight }, "*");
    },
    setComponentValue: function(value) {
        window.parent.postMessage({ type: "streamlit:setComponentValue", value: value }, "*");
    },
    setFrameHeight: function(height) {
        window.parent.postMessage({ type: "streamlit:setFrameHeight", height: height }, "*");
    }
}; 