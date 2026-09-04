// Adds a copy button to every code block.
//
// This is the only JavaScript on the site, which is why it stays this small
// and why it fails quietly. It is loaded with `defer` from the <head> block
// in layouts/_default/baseof.html, so the DOM is parsed by the time it runs.
//
// The button is built here rather than in the render hook so that a reader
// with JavaScript off gets no button at all, instead of one that does
// nothing. Same reason for the navigator.clipboard guard: that API needs a
// secure context, so it is absent over plain http on a LAN address, and a
// button that cannot copy is worse than no button.
//
// The copy is the block's text exactly as rendered, prompts included. Some
// bash blocks here open with `$ ` and the Galileo post has a heredoc whose
// continuation lines start with `> `; stripping those would produce something
// that looks pasteable and is not, so nothing is stripped.
(function () {
  "use strict";
  if (!navigator.clipboard) return;

  document.querySelectorAll(".code-block").forEach(function (block) {
    var code = block.querySelector("pre");
    var head = block.querySelector(".code-head");
    if (!code || !head) return;

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "code-copy";
    btn.textContent = "copy";
    btn.setAttribute("aria-label", "Copy code to clipboard");
    // The label doubles as the status message, so it has to be announced.
    btn.setAttribute("aria-live", "polite");

    var reset;
    btn.addEventListener("click", function () {
      navigator.clipboard.writeText(code.textContent).then(
        function () { btn.textContent = "copied"; },
        function () { btn.textContent = "failed"; }
      );
      clearTimeout(reset);
      reset = setTimeout(function () { btn.textContent = "copy"; }, 1600);
    });

    head.appendChild(btn);
  });
})();
