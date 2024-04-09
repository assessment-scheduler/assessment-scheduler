navbarToggler = document.querySelector(".burger");
navbarMenu = document.querySelector(".links_container_mobile");
navbarLinks = document.querySelectorAll(".mobile_links");
exit = document.querySelector(".exit");

var tl = gsap.timeline({ defaults: { duration: 1, ease: Expo.easeInOut } })
navbarToggler.addEventListener("click", navbarTogglerClick);
tl.paused(true)
tl.to(".links_container_mobile", {
  height: "100%"
});
tl.to("#layout_nav_links_mobile li", {
  opacity: 1,
  stagger: 0.1
}, "-=1");
tl.to("#layout_nav_links_mobile", {
  pointerEvents: "all"
}, "-=1");
tl.to(".exit", {
  opacity: 1,
  y: "5px",
  pointerEvents: "all"
}, "-=1");
function navbarTogglerClick() {
  tl.play();
};
exit.addEventListener('click', () => {
  tl.reverse(.9);
});
navbarLinks.forEach(item => {
  item.addEventListener('click', () => {
    tl.reverse(.9);
  })
});