// Cart badge management functions
async function updateCartBadge() {
  try {
    const response = await fetch("/api/cart/count", {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    if (response.ok) {
      const data = await response.json();
      const cartBadge = document.querySelector(".cart-badge");
      const cartLink = document.querySelector('a[href="/cart"]');

      if (cartLink) {
        // Find existing badge or create new one
        let badge = cartLink.querySelector(".cart-badge");

        if (data.count > 0) {
          if (!badge) {
            // Create new badge structure
            const cartIcon = cartLink.querySelector(".fa-shopping-cart");
            if (cartIcon) {
              // Wrap cart icon in container if not already wrapped
              let iconContainer = cartIcon.parentElement.querySelector(
                ".cart-icon-container"
              );
              if (!iconContainer) {
                iconContainer = document.createElement("div");
                iconContainer.className = "cart-icon-container";
                cartIcon.parentNode.insertBefore(iconContainer, cartIcon);
                iconContainer.appendChild(cartIcon);
              }

              // Create badge
              badge = document.createElement("span");
              badge.className = "cart-badge new-item";
              iconContainer.appendChild(badge);
            }
          }

          if (badge) {
            badge.textContent = data.count;
            badge.className = `cart-badge ${
              data.count >= 10 ? "high-count" : ""
            } ${data.count > 0 ? "has-items" : ""}`;

            // Add bounce animation for new items
            badge.classList.add("new-item");
            setTimeout(() => {
              badge.classList.remove("new-item");
            }, 600);
          }
        } else {
          // Hide badge when cart is empty
          if (badge) {
            badge.className = "cart-badge empty";
            setTimeout(() => {
              badge.remove();
            }, 300);
          }
        }
      }
    }
  } catch (error) {
    console.error("Error updating cart badge:", error);
  }
}

// Enhanced add to cart function
async function addToCartAsync(productId, button) {
  const originalContent = button.innerHTML;

  try {
    // Show loading state
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    button.disabled = true;

    const response = await fetch(`/cart/add/${productId}`, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const data = await response.json();

    if (data.success) {
      // Success feedback
      button.innerHTML = '<i class="fa-solid fa-check"></i>';
      button.classList.add("btn-success");

      // Update cart badge
      await updateCartBadge();

      // Show success message
      showToast(data.message || "Item added to cart!", "success");

      // Reset button after 2 seconds
      setTimeout(() => {
        button.innerHTML = originalContent;
        button.classList.remove("btn-success");
        button.disabled = false;
      }, 2000);
    } else {
      throw new Error(data.message || "Failed to add to cart");
    }
  } catch (error) {
    console.error("Error:", error);

    // Error feedback
    button.innerHTML = '<i class="fa-solid fa-exclamation-triangle"></i>';
    button.classList.add("btn-danger");

    // Show error message
    showToast(error.message || "Failed to add item to cart", "error");

    // Reset button after 2 seconds
    setTimeout(() => {
      button.innerHTML = originalContent;
      button.classList.remove("btn-danger");
      button.disabled = false;
    }, 2000);
  }
}

// Enhanced cart removal function
async function removeFromCartAsync(itemId, button) {
  const originalContent = button.innerHTML;

  try {
    // Show loading state
    button.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
    button.disabled = true;

    const response = await fetch(`/cart/remove/${itemId}`, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },
    });

    const data = await response.json();

    if (data.success) {
      // Update cart badge immediately
      await updateCartBadge();

      // Remove the item from DOM if we're on cart page
      const cartItem = button.closest(".card, .cart-item");
      if (cartItem) {
        cartItem.style.transition = "opacity 0.3s ease";
        cartItem.style.opacity = "0";
        setTimeout(() => {
          cartItem.remove();
          // Check if cart is now empty and update UI accordingly
          const remainingItems = document.querySelectorAll(
            '.card:not([style*="opacity: 0"]), .cart-item:not([style*="opacity: 0"])'
          );
          if (remainingItems.length === 0) {
            location.reload(); // Reload to show empty cart state
          }
        }, 300);
      }

      showToast(data.message || "Item removed from cart", "info");
    } else {
      throw new Error(data.message || "Failed to remove item");
    }
  } catch (error) {
    console.error("Error:", error);
    showToast(error.message || "Failed to remove item from cart", "error");

    // Reset button
    button.innerHTML = originalContent;
    button.disabled = false;
  }
}

// Product card interaction handling
document.addEventListener("DOMContentLoaded", function () {
  // Initialize cart badge on page load
  updateCartBadge();

  // Get all cart buttons (both quick-add and regular)
  const cartButtons = document.querySelectorAll(
    ".quick-add-btn, button[type='submit'][class*='btn'][class*='cart'], button[type='submit'][form*='cart']"
  );

  // Also target forms that submit to cart endpoints
  const cartForms = document.querySelectorAll("form[action*='/cart/add/']");

  // Handle form submissions to cart endpoints
  cartForms.forEach((form) => {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      event.stopPropagation();

      const submitButton = form.querySelector("button[type='submit']");
      if (submitButton) {
        const productId = form.action.split("/cart/add/")[1];
        if (productId) {
          addToCartAsync(productId, submitButton);
        }
      }
    });
  });

  // Handle direct button clicks (for quick-add buttons)
  cartButtons.forEach((button) => {
    button.addEventListener("click", function (event) {
      // Check if this button is inside a form that we've already handled
      const form = this.closest("form");
      if (form && form.action.includes("/cart/add/")) {
        // Let the form handler take care of it
        return;
      }

      // Prevent the default form submission temporarily
      event.preventDefault();
      event.stopPropagation();

      // Get the form element
      if (form) {
        const productId = form.action.split("/cart/add/")[1];
        if (productId) {
          addToCartAsync(productId, this);
        }
      }
    });
  });

  // Handle any additional cart buttons that might be added dynamically
  document.addEventListener("click", function (event) {
    if (
      event.target.matches('button[type="submit"]') &&
      event.target.closest('form[action*="/cart/add/"]')
    ) {
      const form = event.target.closest("form");
      if (form && !form.hasAttribute("data-cart-handled")) {
        event.preventDefault();
        event.stopPropagation();

        form.setAttribute("data-cart-handled", "true");
        const productId = form.action.split("/cart/add/")[1];
        if (productId) {
          addToCartAsync(productId, event.target);
        }
      }
    }
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
