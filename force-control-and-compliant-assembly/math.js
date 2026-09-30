document.addEventListener("DOMContentLoaded", () => {
  const render = () => {
    if (!window.renderMathInElement) return;
    renderMathInElement(document.body, {
      delimiters: [
        {left: "\\[", right: "\\]", display: true},
        {left: "\\(", right: "\\)", display: false}
      ],
      throwOnError: false
    });
  };
  if (window.renderMathInElement) render();
  else window.addEventListener("load", render, {once: true});
});
