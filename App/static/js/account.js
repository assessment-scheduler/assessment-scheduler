const searchInput = document.getElementById("search_box");
const searchDropdown = document.getElementById("search-dropdown");
const selectedCourses = document.getElementById("selected_courses");

const coursesUrl = "/get_courses";

function getCourses() {
  fetch(coursesUrl)
    .then(response => response.json()) // Parse JSON response
    .then(data => {
      courses = data; // Assuming your route returns an array of courses
      handleSearch(); // Call handleSearch to populate dropdown with retrieved courses
    })
    .catch(error => console.error(error)); // Handle errors if any
}

function handleSearch(e) {
  e.preventDefault(); // Prevent form submission

  const searchTerm = searchInput.value.toLowerCase();
  const filteredCourses = courses.filter((course) => course.toLowerCase().includes(searchTerm));

  searchDropdown.innerHTML = ""; // Clear previous results

  if (filteredCourses.length > 0) {
    const dropdownList = document.createElement("ul");
    dropdownList.style.listStyleType = "none";
    
    filteredCourses.forEach((course) => {
      const listItem = document.createElement("li");
      listItem.textContent = course;

      // Check if course already selected before adding click event listener
      if (!selectedCourses.textContent.includes(course)) {
        listItem.addEventListener("click", () => addCourse(course));
      }

      dropdownList.appendChild(listItem);
    });

    searchDropdown.appendChild(dropdownList);
    searchDropdown.style.display = "block"; // Show dropdown
  } else {
    searchDropdown.style.display = "none"; // Hide dropdown if no results
  }
}

function addCourse(course) {
  const courseElement = document.createElement("p");
  courseElement.textContent = course;
  courseElement.classList.add("selected-course");
  selectedCourses.appendChild(courseElement);

  // Clear search input and hide dropdown
  searchInput.value = "";
  searchDropdown.style.display = "none";
}

getCourses();

searchInput.addEventListener("keyup", handleSearch);