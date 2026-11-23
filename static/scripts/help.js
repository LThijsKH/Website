"use strict";

// AI disclosure: this file was reworked with the help of opus 5.5

// "How to navigate" panel on the photo pages (templates/_photo_help.html)
const helpPopup = document.getElementById("help-popup");

function openHelp() {
  helpPopup?.classList.remove("hidden");
}

function closeHelp() {
  helpPopup?.classList.add("hidden");
  try {
    localStorage.setItem("seenPhotoHelp", "true");
  } catch {}
}

window.openHelp = openHelp;
window.closeHelp = closeHelp;

// Esc closes the panel. This runs before gallery.js's key handler (help.js is
// loaded first), so stop the event there: otherwise the same Esc would also
// step back a view on the photo page.
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && helpPopup && !helpPopup.classList.contains("hidden")) {
    closeHelp();
    e.stopImmediatePropagation();
  }
});
