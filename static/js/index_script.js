/*=============== SWIPER JS ===============*/
let swiperCards = new Swiper(".card__content", {
  effect: 'coverflow',
  loop: true,
  spaceBetween: 24,
  grabCursor: true,
  a11y: true,
  centeredSlides: true,
  keyboard: { enabled: true },
  coverflowEffect: {
    rotate: 0,
    stretch: 0,
    depth: 100,
    modifier: 2.5,
  },
  pagination: {
    el: ".swiper-pagination",
    clickable: true,
    dynamicBullets: true,
  },

  navigation: {
    nextEl: ".swiper-button-next",
    prevEl: ".swiper-button-prev",
  },

  breakpoints: {
    0: { slidesPerView: 1 },
    600: { slidesPerView: 2 },
    968: { slidesPerView: 3 },
  },
});

// expose for modal/updater
window.swiperCards = swiperCards;

// flip behavior
document.addEventListener('click', (e) => {
  const card = e.target.closest('.card-item');
  if (!card) return;
  if (e.target.closest('.swiper-button-next') || e.target.closest('.swiper-button-prev')) return;
  card.classList.toggle('flipped');
});

document.addEventListener('keydown', (e) => {
  const el = document.activeElement;
  if (!el || !el.classList) return;
  if (!el.classList.contains('card-item')) return;
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    el.classList.toggle('flipped');
  }
});

swiperCards.on('slideChange', () => {
  document.querySelectorAll('.card-item.flipped').forEach(c => c.classList.remove('flipped'));
});