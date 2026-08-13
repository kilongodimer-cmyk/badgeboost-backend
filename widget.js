(function () {
  // 1. Récupération de la clé API depuis la balise script
  const currentScript = document.currentScript;
  const apiKey = currentScript ? currentScript.getAttribute("data-api-key") : null;

  if (!apiKey) {
    console.error("BadgeBoost: Clé API manquante dans data-api-key.");
    return;
  }

  // 2. Requête vers ton API FastAPI Render
  fetch(`https://badgeboost-backend.onrender.com/api/v1/widget/${apiKey}`)
    .then((response) => {
      if (!response.ok) throw new Error("Clé API invalide ou erreur serveur");
      return response.json();
    })
    .then((data) => {
      // 3. Création du container HTML du badge
      const badgeDiv = document.createElement("div");
      badgeDiv.id = "badgeboost-container";
      badgeDiv.style.cssText = `
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background-color: #f3f4f6;
        color: #1f2937;
        padding: 8px 14px;
        border-radius: 20px;
        font-family: system-ui, sans-serif;
        font-size: 14px;
        font-weight: 500;
        border: 1px solid #e5e7eb;
        margin: 10px 0;
      `;

      badgeDiv.innerHTML = `
        <span>🛡️</span>
        <span>${data.badge_text}</span>
        ${data.show_branding ? '<span style="font-size:10px; color:#9ca3af; margin-left:6px;">by BadgeBoost</span>' : ''}
      `;

      // Injecter le badge sur la page du client
      const targetElement = document.getElementById("badgeboost-widget") || document.body;
      targetElement.appendChild(badgeDiv);
    })
    .catch((err) => console.error("BadgeBoost Error:", err));
})();
