function triggerPreset(preset) {
    fetch(`/preset/${preset}`, {
        method: "POST"
    })
    .then(response => response.json())
    .then(data => console.log(data))
    .catch(err => console.error(err));
}