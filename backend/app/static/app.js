const state = {
  location: null,
};

const spotlight = document.getElementById("spotlight");
const resultContainer = document.getElementById("results");
const resultCaption = document.getElementById("result-caption");
const form = document.getElementById("search-form");

function statusClass(status) {
  return `status-${status.state}`;
}

function formatStatus(status) {
  if (!status) {
    return "Unknown";
  }
  if (status.freshness_minutes == null) {
    return status.label;
  }
  return `${status.label} • updated ${status.freshness_minutes} min ago`;
}

function formatPrice(service) {
  if (service.price_min == null && service.price_max == null) {
    return service.supports_home_visit ? "Home service" : "Price on request";
  }
  if (service.price_min != null && service.price_max != null) {
    return `INR ${service.price_min} - ${service.price_max}`;
  }
  return `INR ${service.price_min ?? service.price_max}`;
}

function buildCallLink(shop) {
  return `tel:${shop.whatsapp_number || shop.owner_phone}`;
}

function buildWhatsAppLink(shop) {
  const digits = (shop.whatsapp_number || shop.owner_phone || "").replace(/\D/g, "");
  return `https://wa.me/${digits}`;
}

function renderResults(results) {
  resultContainer.innerHTML = "";
  if (!results.length) {
    resultContainer.innerHTML = "<p>No shops found yet for that search.</p>";
    return;
  }

  const template = document.getElementById("result-card-template");
  for (const shop of results) {
    const node = template.content.firstElementChild.cloneNode(true);
    const statusChip = node.querySelector(".status-chip");
    statusChip.textContent = formatStatus(shop.current_status);
    statusChip.classList.add(statusClass(shop.current_status));
    node.querySelector("h3").textContent = shop.display_name;
    node.querySelector(".meta").textContent = `${shop.category} • ${shop.pincode}${shop.distance_km ? ` • ${shop.distance_km} km` : ""}`;
    node.querySelector(".addr").textContent = shop.address || "Address coming soon";
    node.querySelector(".open-link").href = shop.public_url;
    node.querySelector(".call-link").href = buildCallLink(shop);
    node.querySelector(".wa-link").href = buildWhatsAppLink(shop);
    resultContainer.appendChild(node);
  }
}

function renderSpotlight(shop) {
  spotlight.classList.remove("hidden");
  const fallbackHtml = shop.fallbacks.length
    ? shop.fallbacks
        .map(
          (fallback) => `
            <div class="fallback-row">
              <div>
                <strong>${fallback.display_name}</strong>
                <div class="small">${fallback.category}${fallback.distance_km ? ` • ${fallback.distance_km} km` : ""}</div>
              </div>
              <a class="inline-btn" href="${fallback.public_url}">Open</a>
            </div>
          `
        )
        .join("")
    : "<p class=\"small\">No fallback shops added yet.</p>";

  const servicesHtml = shop.services
    .map(
      (service) => `
        <div class="service-row">
          <div>
            <strong>${service.name}</strong>
            <div class="small">${service.supports_home_visit ? "Home visit available" : "In-shop service"}</div>
          </div>
          <span>${formatPrice(service)}</span>
        </div>
      `
    )
    .join("");

  const subscribeButton =
    shop.current_status.state === "open"
      ? ""
      : `<button id="notify-btn" class="inline-btn primary" type="button">Notify me when it reopens</button>`;

  spotlight.innerHTML = `
    <div class="spotlight-head">
      <div>
        <div class="status-chip ${statusClass(shop.current_status)}">${formatStatus(shop.current_status)}</div>
        <h2>${shop.display_name}</h2>
        <p>${shop.category} • ${shop.address || "Bengaluru"} • ${shop.pincode}</p>
      </div>
      <div class="actions">
        <a href="${buildCallLink(shop)}">Call</a>
        <a href="${buildWhatsAppLink(shop)}" target="_blank">WhatsApp</a>
        <a href="${shop.payment_plan?.payment_link || "#"}" target="_blank">Pay plan</a>
      </div>
    </div>
    <div class="detail-grid">
      <section class="detail-card">
        <h3>Services</h3>
        <div class="service-list">${servicesHtml}</div>
      </section>
      <section class="detail-card">
        <h3>If this shop is closed</h3>
        <div class="fallback-list">${fallbackHtml}</div>
        <div class="actions">${subscribeButton}</div>
      </section>
    </div>
  `;

  const notifyButton = document.getElementById("notify-btn");
  if (notifyButton) {
    notifyButton.addEventListener("click", async () => {
      const userContact = window.prompt("Enter your phone or WhatsApp number");
      if (!userContact) {
        return;
      }
      await fetch(`/v1/notifications/reopen/${shop.id}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_contact: userContact, channel: "web" }),
      });
      notifyButton.textContent = "We will notify you";
      notifyButton.disabled = true;
    });
  }
}

async function fetchShop(identifier) {
  const response = await fetch(`/v1/shops/public/${encodeURIComponent(identifier)}`);
  if (!response.ok) {
    throw new Error("Shop not found");
  }
  const shop = await response.json();
  renderSpotlight(shop);
}

async function runSearch(query, pin) {
  const params = new URLSearchParams();
  if (query) params.set("q", query);
  if (pin) params.set("pin", pin);
  if (state.location) {
    params.set("lat", state.location.lat);
    params.set("lng", state.location.lng);
  }
  const response = await fetch(`/v1/shops/search?${params.toString()}`);
  const payload = await response.json();
  resultCaption.textContent = payload.total
    ? `${payload.total} shop${payload.total === 1 ? "" : "s"} found`
    : "No matches yet";
  renderResults(payload.results || []);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const query = document.getElementById("query").value.trim();
  const pin = document.getElementById("pin").value.trim();
  await runSearch(query, pin);
});

document.getElementById("use-location").addEventListener("click", () => {
  if (!navigator.geolocation) {
    return;
  }
  navigator.geolocation.getCurrentPosition((position) => {
    state.location = {
      lat: position.coords.latitude,
      lng: position.coords.longitude,
    };
    resultCaption.textContent = "Using your live location for fallback ranking.";
  });
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/service-worker.js").catch(() => null);
}

const pathParts = window.location.pathname.split("/").filter(Boolean);
if (pathParts[0] === "s" && pathParts[1]) {
  fetchShop(decodeURIComponent(pathParts[1])).catch(() => {
    resultCaption.textContent = "That shop page could not be loaded.";
  });
} else {
  runSearch("", "");
}
