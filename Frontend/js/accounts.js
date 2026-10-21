(function () {
  "use strict";

  document.querySelectorAll(".pw-toggle").forEach(function (button) {
    button.addEventListener("click", function () {
      var input = document.getElementById(button.getAttribute("aria-controls"));
      if (!input) return;

      var reveal = input.type === "password";
      input.type = reveal ? "text" : "password";
      button.textContent = reveal ? "Hide" : "Show";
      button.setAttribute("aria-pressed", String(reveal));
      button.setAttribute(
        "aria-label",
        (reveal ? "Hide " : "Show ") + (button.dataset.label || "password")
      );
    });
  });
})();
