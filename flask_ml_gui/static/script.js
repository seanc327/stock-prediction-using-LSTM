document.addEventListener("DOMContentLoaded", function () {
    const text = "Stock Predictor";
    let index = 0;
    const speed = 100; // speed setting for typewriter animation

    function typeWriter() {
        if (index < text.length) {
            document.getElementById("typewriter").innerHTML += text.charAt(index);
            index++;
            setTimeout(typeWriter, speed);
        } else {
            // removing cursor
            document.getElementById("typewriter").style.borderRight = "none";
        }
    }

    typeWriter();

    // progress loading
    document.getElementById("upload-form").addEventListener("submit", function () {
        document.getElementById("loading").style.display = "block";
    });
});
