async function testCamera(index) {

    const response = await fetch(`/test-camera/${index}`, {
        method: "POST"
    });

    const result = await response.json();

    const status = document.getElementById(`status-${index}`);

    if (result.status === "ok") {
        status.innerHTML = "🟢 Online";
    }
    else {
        status.innerHTML = "🔴 " + result.message;
    }

}