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
