document.getElementById('btn').addEventListener('click', handleSubmit);

function handleSubmit() {
    const origin = document.getElementById('origin').value.trim();
    const destination = document.getElementById('destination').value.trim();
    const departure = document.getElementById('departure_time').value.trim();

    if (!origin || !destination) {
        alert('Please fill in origin and destination.');
        return;
    }

    console.log({ origin, destination, departure });
}