const map = L.map("map").setView([47.7961287, 3.570579], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

let vegetableIcon = L.icon({
  iconUrl: "../static/icons/plante.png",
  iconSize: [25, 25],
  popupAnchor: [1, 1],
});

markersData.forEach(async function (markerData) {
  try {
    const { latitude, longitude, adresse, pseudo, nom } = markerData;

    let newMarker = L.marker([latitude, longitude], {
      icon: vegetableIcon,
    }).addTo(map);

    newMarker.bindPopup(
      `<b>${adresse}</b><br/>Propriétaire: ${pseudo}<br/>Espèce: ${nom}<br/>`
    );
  } catch (error) {
    console.error(
      "Erreur de géocodage pour l'adresse:",
      markerData.adresse,
      error
    );
  }
});
