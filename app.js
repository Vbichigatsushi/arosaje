// Sélectionner toutes les sections et les liens de navigation
const sections = document.querySelectorAll(".section");
const links = document.querySelectorAll(".footer-link");

// Ajouter l'événement de clic sur chaque lien du footer
links.forEach((link) => {
  link.addEventListener("click", (e) => {
    e.preventDefault();

    // Masquer toutes les sections
    sections.forEach((section) => section.classList.remove("active"));

    // Récupérer l'ID de la section cible à partir du lien
    const targetId = link.getAttribute("href").substring(1);
    const targetSection = document.getElementById(targetId);

    // Afficher section si elle existe
    if (targetSection) {
      targetSection.classList.add("active");
    }

    if (targetId === "map") {
      console.log("map init");
      setTimeout(function () {
        map.invalidateSize();
      }, 200);
    }
  });
});

// Démarrage de la page: acceuil par défaut

document.getElementById("accueil").classList.add("active");

// Partie Map

let map;

document.addEventListener("DOMContentLoaded", function () {
  map = L.map("map-container").setView([48.8566, 2.3522], 13);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
  }).addTo(map);

  let vegetableIcon = L.icon({
    iconUrl: "./icon/plante.png",
    iconSize: [25, 25],
    popupAnchor: [1, -34],
  });

  async function geocodeAddress(address) {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
      address
    )}`;

    const response = await fetch(url);
    const data = await response.json();

    if (data.length > 0) {
      const { lat, lon } = data[0];
      return { lat: parseFloat(lat), lon: parseFloat(lon) };
    } else {
      throw new Error("Adresse introuvable");
    }
  }

  const searchBtn = document.getElementById("searchButton");

  searchBtn.addEventListener("click", async () => {
    const address = document.getElementById("addressInput").value.trim();

    if (!address) {
      alert(
        "Veuillez entrer une adresse, exemple: '1 place du Maréchal Leclerc, Auxerre, France' ."
      );
      return;
    }

    try {
      const { lat, lon } = await geocodeAddress(address);

      const marker = L.marker([lat, lon], { icon: vegetableIcon }).addTo(map);
      marker.bindPopup(`<b>${address}</b>`).openPopup();

      map.setView([lat, lon], 16);
    } catch (error) {
      alert(`Erreur : Adresse introuvable.Veuillez vérifier la validité de l'adresse.
      Exemple: 1 place du Maréchal Leclerc, Auxerre, France`);
    }
  });
});
