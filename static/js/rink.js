function triggerPreset(preset) {
  fetch(`/camera/1/preset/${preset}`, {
    method: "POST"
  })
  .then(() => console.log(`Preset ${preset} triggered`))
  .catch(err => console.error(err));
}
