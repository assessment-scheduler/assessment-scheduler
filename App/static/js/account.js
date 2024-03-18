const searchBox = document.getElementById('search_box');
const searchDropdown = document.getElementById('search-dropdown');
const selectedCoursesList = document.getElementById('selected_courses');

searchBox.addEventListener('keyup', function(event) {
  const searchQuery = event.target.value.toLowerCase();
  const courses = ['comp1601', 'comp1600', 'comp2602', 'comp2603', 'info3604'];

  const searchedCourses = courses.filter(course => course.toLowerCase().includes(searchQuery));

  // Clear previous search results
  searchDropdown.querySelector('ul').innerHTML = "";

  if (searchedCourses.length > 0) {
    // Create list items for matching courses
    const resultList = document.createElement('ul');
    searchedCourses.forEach(course => {
      const listItem = document.createElement('li');
      listItem.textContent = course;  // Use the course code directly
      resultList.appendChild(listItem);
    });
    searchDropdown.querySelector('ul').appendChild(resultList);
    searchDropdown.style.display = 'block';  // Show the dropdown
  } else {
    searchDropdown.style.display = 'none';  // Hide the dropdown
  }
});

// Handle potential clicks outside the dropdown (to close it)
document.addEventListener('click', function(event) {
  if (!searchDropdown.contains(event.target)) {
    searchDropdown.style.display = 'none';
  }
});

// Handle adding courses to "My Courses"
searchDropdown.addEventListener('click', function(event) {
    if (event.target.tagName === 'LI') {  // Check if a list item was clicked
      const courseCode = event.target.textContent.trim();  // Get course code
      const selectedCourses = getSelectedCourses(); // Get existing selected courses (implementation provided below)
  
      if (!selectedCourses.includes(courseCode)) {  // Check if course is not already selected
        const newCourse = document.createElement('p');
        newCourse.textContent = courseCode;
        selectedCoursesList.appendChild(newCourse);
        console.log(newCourse)
        // Update selected courses storage (implementation depends on your storage method)
        setSelectedCourses([...selectedCourses, courseCode]);
      }
    }
  });
  
  // Function to get existing selected courses (replace with your storage logic)
  function getSelectedCourses() {
    // Replace with your logic to retrieve selected courses from localStorage, cookies, or database
    // This example assumes localStorage:
    return localStorage.getItem('selectedCourses')?.split(',') || [];
  }
  
  // Function to update selected courses storage (replace with your storage logic)
  function setSelectedCourses(courses) {
    // Replace with your logic to save courses to localStorage, cookies, or database
    // This example assumes localStorage:
    localStorage.setItem('selectedCourses', courses.join(','));
  }

