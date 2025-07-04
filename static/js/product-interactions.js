// Product card interaction handling
document.addEventListener("DOMContentLoaded", function () {
  // Get all cart buttons
  const cartButtons = document.querySelectorAll(".quick-add-btn");

  cartButtons.forEach((button) => {
    button.addEventListener("click", function (event) {
      // Prevent the default form submission temporarily
      event.preventDefault();

      // Stop the event from bubbling up to parent elements
      event.stopPropagation();

      // Get the form element
      const form = this.closest("form");

      // Submit the form programmatically
      if (form) {
        // Add visual feedback
        const originalContent = this.innerHTML;
        this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        this.disabled = true;

        // Create FormData and submit via fetch
        const formData = new FormData(form);

        fetch(form.action, {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        })
          .then((response) => {
            if (response.ok) {
              // Success feedback
              this.innerHTML = '<i class="fa-solid fa-check"></i>';
              this.classList.add("btn-success");

              // Reset button after 2 seconds
              setTimeout(() => {
                this.innerHTML = originalContent;
                this.classList.remove("btn-success");
                this.disabled = false;
              }, 2000);

              // Show success message (optional)
              showToast("Item added to cart!", "success");
            } else {
              throw new Error("Failed to add to cart");
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            // Error feedback
            this.innerHTML = '<i class="fa-solid fa-exclamation-triangle"></i>';
            this.classList.add("btn-danger");

            // Reset button after 2 seconds
            setTimeout(() => {
              this.innerHTML = originalContent;
              this.classList.remove("btn-danger");
              this.disabled = false;
            }, 2000);

            // Show error message (optional)
            showToast("Failed to add item to cart", "error");
          });
      }
    });
  });
});

// Simple toast notification function (optional)
function showToast(message, type = "info") {
  // Create toast element
  const toast = document.createElement("div");
  toast.className = `toast-notification toast-${type}`;
  toast.textContent = message;

  // Style the toast
  Object.assign(toast.style, {
    position: "fixed",
    top: "20px",
    right: "20px",
    backgroundColor:
      type === "success" ? "#16a34a" : type === "error" ? "#dc2626" : "#219ebc",
    color: "white",
    padding: "12px 20px",
    borderRadius: "8px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
    zIndex: "9999",
    fontSize: "14px",
    fontWeight: "500",
    transform: "translateX(100%)",
    transition: "transform 0.3s ease",
  });

  // Add to document
  document.body.appendChild(toast);

  // Animate in
  setTimeout(() => {
    toast.style.transform = "translateX(0)";
  }, 100);

  // Remove after 3 seconds
  setTimeout(() => {
    toast.style.transform = "translateX(100%)";
    setTimeout(() => {
      document.body.removeChild(toast);
    }, 300);
  }, 3000);
}
