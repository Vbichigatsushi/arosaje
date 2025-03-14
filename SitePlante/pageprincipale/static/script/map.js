const plantesList = document.querySelector("#plantes-list");
const messageContainer = document.querySelector("#no-data-message");

if (markersData.length === 0) {
  messageContainer.textContent = "Aucune demande dans les environs.";
  messageContainer.style.display = "block";
} else {
  messageContainer.style.display = "none";

  markersData.forEach((marker) => {
    const card = document.createElement("div");
    card.classList.add("plante-card");

    const pseudo = document.createElement("h3");
    pseudo.textContent = marker.pseudo;
    card.appendChild(pseudo);

    const planteNom = document.createElement("p");
    planteNom.textContent = `Plante : ${marker.nom}`;
    card.appendChild(planteNom);

    const distance = document.createElement("p");

    let distanceText = "";
    if (marker.distance <= 100) {
      distanceText = "Moins de 100 mètres.";
    } else if (marker.distance > 100 && marker.distance <= 200) {
      distanceText = "Moins de 200 mètres.";
    } else if (marker.distance > 200 && marker.distance <= 300) {
      distanceText = "Moins de 100 mètres.";
    } else if (marker.distance > 300 && marker.distance <= 400) {
      distanceText = "Moins de 100 mètres.";
    } else if (marker.distance > 400 && marker.distance <= 500) {
      distanceText = "Moins de 100 mètres.";
    }
    distance.textContent = `Distance : ${distanceText}`;
    card.appendChild(distance);

    plantesList.appendChild(card);
  });
}

const map = L.map("map").setView([47.7961287, 3.570579], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

let vegetableIcon = L.icon({
  iconUrl: "../static/icons/plante.png",
  iconSize: [25, 25],
  popupAnchor: [1, 1],
});

console.log("Données des marqueurs:", markersData);

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
