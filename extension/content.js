console.log("Content script loaded!"); // Check if script is loading

let socket = new WebSocket("ws://localhost:8080");
let lastElement = null;

document.addEventListener("mousemove", (e) => {
  const element = document.elementFromPoint(e.clientX, e.clientY);
  if (element !== lastElement) {
    lastElement = element;
    const elementInfo = {
      type: "element_data",
      data: {
        tagName: element.tagName,
        id: element.id,
        className: element.className,
        href: element.href || null,
        innerText: element.innerText?.substring(0, 100), // Truncate long text
        value: element.value,
        path: getElementPath(element),
        url: window.location.href,
        domain: window.location.hostname,
        position: {
          x: e.clientX,
          y: e.clientY,
        },
        attributes: getElementAttributes(element),
      },
    };
    socket.send(JSON.stringify(elementInfo));
  }
});

// Helper functions
function getElementPath(element) {
  const path = [];
  while (element && element.nodeType === Node.ELEMENT_NODE) {
    let selector = element.tagName.toLowerCase();
    if (element.id) {
      selector += `#${element.id}`;
      path.unshift(selector);
      break;
    } else {
      let sibling = element;
      let nth = 1;
      while (sibling.previousElementSibling) {
        sibling = sibling.previousElementSibling;
        if (sibling.tagName === element.tagName) nth++;
      }
      if (nth > 1) selector += `:nth-of-type(${nth})`;
    }
    path.unshift(selector);
    element = element.parentNode;
  }
  return path.join(" > ");
}

function getElementAttributes(element) {
  const attributes = {};
  for (const attr of element.attributes) {
    attributes[attr.name] = attr.value;
  }
  return attributes;
}
