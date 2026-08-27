// Auto-dismiss alerts after 4 seconds
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".alert").forEach(function (alert) {
        setTimeout(function () {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 4000);
    });

    // Quantity stepper on menu item cards (updates hidden qty input before add-to-cart submit)
    document.querySelectorAll(".qty-stepper").forEach(function (stepper) {
        var input = stepper.querySelector(".qty-value");
        stepper.querySelectorAll(".qty-btn").forEach(function (btn) {
            btn.addEventListener("click", function () {
                var current = parseInt(input.value || "1", 10);
                if (btn.dataset.action === "inc") current += 1;
                if (btn.dataset.action === "dec") current = Math.max(1, current - 1);
                input.value = current;
            });
        });
    });
});
