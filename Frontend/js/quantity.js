(function () {
  "use strict";

  document.querySelectorAll(".qty").forEach(function (group) {
    var input = group.querySelector('input[name="quantity"]');
    if (!input) return;

    group.querySelectorAll("button[data-step]").forEach(function (button) {
      button.addEventListener("click", function () {
        var current = Number(input.value);
        var minimum = Number(input.min || 1);
        var maximum = Number(input.max || Number.MAX_SAFE_INTEGER);
        var next = Math.min(maximum, Math.max(minimum, current + Number(button.dataset.step)));
        if (next !== current) {
          input.value = String(next);
          group.requestSubmit();
        }
      });
    });
  });
})();
