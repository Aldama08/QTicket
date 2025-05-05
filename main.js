
  document.getElementById('loginBtn').addEventListener('click', function (e) {
    e.preventDefault(); // evita que se envíe el formulario por defecto

    const form = document.getElementById('loginForm');

    if (!form.checkValidity()) {
      alert('Por favor, completa todos los campos requeridos.');
      return;
    }

    // Mostrar modal 
    const myModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    myModal.show();

    // Simula 3 seg y luego redirige
    setTimeout(() => {
      window.location.href = "register.html";
    }, 3000);

  // CAMPUS
  const campusItems = document.querySelectorAll('#campusDropdown + .dropdown-menu .dropdown-item');
  const campusButton = document.getElementById('campusDropdown');
  const selectedCampusInput = document.getElementById('selectedCampus');

  campusItems.forEach(item => {
    item.addEventListener('click', () => {
      campusButton.textContent = item.textContent; // Cambiar el texto del botón
      selectedCampusInput.value = item.textContent; // Guardar la selección en el input oculto

      // Resaltar la opción seleccionada
      campusItems.forEach(i => i.classList.remove('active')); // Quitar 'active' de todas las opciones
      item.classList.add('active'); // Agregar 'active' a la opción seleccionada
    });
  });

  // CARRERA
  const carreraItems = document.querySelectorAll('#careerDropdown + .dropdown-menu .dropdown-item');
  const carreraButton = document.getElementById('careerDropdown');
  const selectedCarreraInput = document.getElementById('selectedCarrera');

  carreraItems.forEach(item => {
    item.addEventListener('click', () => {
      carreraButton.textContent = item.textContent; // Cambiar el texto del botón
      selectedCarreraInput.value = item.textContent; // Guardar la selección en el input oculto

      // Resaltar la opción seleccionada
      carreraItems.forEach(i => i.classList.remove('active')); // Quitar 'active' de todas las opciones
      item.classList.add('active'); // Agregar 'active' a la opción seleccionada
    });
  });
  });

