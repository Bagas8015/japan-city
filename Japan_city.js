//agar navbar tetap fixed saat di scroll
let navbar = document.getElementsByTagName("nav")[0];
let offsetTopNavbar = navbar.offsetTop;

window.onscroll = function () {
  if (this.pageYOffset >= offsetTopNavbar) {
    navbar.classList.add("sticky");
  } else {
    navbar.classList.remove("sticky");
  }
};
