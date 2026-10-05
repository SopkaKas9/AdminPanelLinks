document.documentElement.classList.add("js");

document.addEventListener("click", (event) => {
  const copyBtn = event.target.closest("[data-copy]");
  if (copyBtn) {
    navigator.clipboard.writeText(copyBtn.dataset.copy).then(() => {
      const original = copyBtn.textContent;
      copyBtn.textContent = "Скопировано";
      setTimeout(() => { copyBtn.textContent = original; }, 1500);
    });
    return;
  }

  const removeBtn = event.target.closest("[data-remove]");
  if (removeBtn) {
    const row = removeBtn.closest("[data-item-row]");
    const checkbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
    if (checkbox) checkbox.checked = true;
    row.hidden = true;
  }
});

const container = document.getElementById("items");
if (container) {
  const prefix = container.dataset.prefix;
  const total = document.getElementById(`id_${prefix}-TOTAL_FORMS`);
  const template = document.getElementById("empty-row");

  document.getElementById("add-item").addEventListener("click", () => {
    const index = parseInt(total.value, 10);
    container.insertAdjacentHTML("beforeend", template.innerHTML.replace(/__prefix__/g, index));
    total.value = index + 1;
  });
}
