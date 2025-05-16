// Table sorting & filtering
document.addEventListener("DOMContentLoaded", () => {
  const table   = document.querySelector("table[data-sortable]");
  const headers = table.querySelectorAll("th");
  const rows    = Array.from(table.tBodies[0].rows);
  const search  = document.getElementById("searchBox");

  let sortCol = -1, sortDir = 1;

  headers.forEach((th, idx) => {
    th.addEventListener("click", () => {
      if (sortCol === idx) sortDir *= -1;
      else { sortCol = idx; sortDir = 1; }

      headers.forEach(h => h.classList.remove("sort-asc", "sort-desc"));
      th.classList.add(sortDir === 1 ? "sort-asc" : "sort-desc");

      rows.sort((a, b) => {
        let vA = a.cells[idx].innerText.toLowerCase();
        let vB = b.cells[idx].innerText.toLowerCase();
        return vA > vB ? sortDir : vA < vB ? -sortDir : 0;
      });
      rows.forEach(r => table.tBodies[0].appendChild(r));
    });
  });

  search.addEventListener("input", () => {
    const term = search.value.toLowerCase();
    rows.forEach(r => {
      r.style.display = r.innerText.toLowerCase().includes(term) ? "" : "none";
    });
  });

  // Capture public IP and inject into forms
  (async () => {
    try {
      let ip = sessionStorage.getItem("pubIP");
      if (!ip) {
        const res = await fetch("https://api.ipify.org?format=json");
        ip = (await res.json()).ip;
        sessionStorage.setItem("pubIP", ip);
      }
      document.querySelectorAll("form.needs-ip").forEach(f => {
        let hid = f.querySelector("input[name='client_ip']");
        if (!hid) {
          hid = document.createElement("input");
          hid.type = "hidden";
          hid.name = "client_ip";
          f.appendChild(hid);
        }
        hid.value = ip;
      });
    } catch (e) {
      console.warn("Could not fetch public IP", e);
    }
  })();
});
