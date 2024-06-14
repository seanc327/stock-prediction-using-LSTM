document.addEventListener("DOMContentLoaded", function () {
    const text = "Stock Predictor";
    let index = 0;
    const speed = 100; // Adjust the speed of the typing effect

    function typeWriter() {
        if (index < text.length) {
            document.getElementById("typewriter").innerHTML += text.charAt(index);
            index++;
            setTimeout(typeWriter, speed);
        } else {
            // Remove the blinking cursor after typing is done
            document.getElementById("typewriter").style.borderRight = "none";
        }
    }

    typeWriter();

    document.getElementById("upload-form").addEventListener("submit", function () {
        document.getElementById("loading").style.display = "block";
    });
});
