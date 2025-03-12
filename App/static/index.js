var weekCounter = 0;

document.addEventListener("DOMContentLoaded", function () {
  const colors = {
    Assignment: "#3397b9",
    Quiz: "#499373",
    Project: "#006064",
    Exam: "#CC4E4E",
    Presentation: "#cc7a50",
    Other: "#C29203",
    Pending: "#999999",
    Proctored: "#8B4513"
  };

  const calendarEvents = [];
  renderCourses(myCourses, exams);
  const levelFilter = document.getElementById("level");
  const courseFilter = document.getElementById("courses");
  const typeFilter = document.getElementById("assignmentType");

  const calendarEl = document.getElementById("calendar");
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    headerToolbar: {
      left: "prev,next,today",
      center: "title",
      right: "semesterView,dayGridMonth,timeGridWeek,timeGridDay",
    },
    views: {
      semesterView: {
        type: "dayGridMonth",
        duration: { weeks: semesterWeeks },
        buttonText: "Semester",
        visibleRange: {
          start: semester.start_date,
          end: semester.end_date,
        },
      },
    },
    allDaySlot: false,
    slotMinTime: "08:00:00",
    slotMaxTime: "20:00:00",
    editable: true,
    selectable: true,
    droppable: true,
    events: calendarEvents,
    eventResize: handleEventEdit,
    eventDrop: handleEventEdit,
    drop: handleNewItem,
  });
  calendar.render();

  levelFilter.addEventListener("change", function () {
    const selectedLevel = levelFilter.value;
    const selectedCourse = courseFilter.value;
    const selectedType = typeFilter.value;
    const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
    updateCalendarEvents(calendar, filteredEvents);
  });

  courseFilter.addEventListener("change", function () {
    const selectedLevel = levelFilter.value;
    const selectedCourse = courseFilter.value;
    const selectedType = typeFilter.value;
    const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
    updateCalendarEvents(calendar, filteredEvents);
  });

  typeFilter.addEventListener("change", function () {
    const selectedLevel = levelFilter.value;
    const selectedCourse = courseFilter.value;
    const selectedType = typeFilter.value;
    const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
    updateCalendarEvents(calendar, filteredEvents);
  });

  function renderCourses(courses, assessments) {
    const containerEl = document.getElementById("courses-list");
    containerEl.innerHTML = '';
    
    courses.forEach((course) => {
      const courseCard = document.createElement("div");
      courseCard.classList.add("course-card");

      const title = document.createElement("h3");
      title.textContent = course.code + ": " + course.name;
      courseCard.appendChild(title);

      const eventsContainer = document.createElement("div");
      eventsContainer.classList.add("course-events");

      // Filter assessments for this course
      const courseAssessments = assessments.filter((a) => a.course_code === course.code);
      
      courseAssessments.forEach((assessment) => {
        const eventEl = createEventElement(assessment, course.code, colors);
        
        // If the assessment has scheduled dates, add it to calendar events
        if (assessment.scheduled) {
          const eventObj = createEventObject(assessment, colors);
          calendarEvents.push(eventObj);
        } else if (assessment.start_week && assessment.start_day) {
          // Convert week/day to actual date and add to calendar
          const startDate = getDateFromWeekDay(semesterStartDate, assessment.start_week, assessment.start_day);
          const endDate = assessment.end_week && assessment.end_day ? 
                          getDateFromWeekDay(semesterStartDate, assessment.end_week, assessment.end_day) : 
                          startDate;
          
          const eventObj = {
            id: assessment.id,
            title: `${course.code} - ${assessment.name} (${assessment.percentage}%)`,
            backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
            start: startDate,
            end: endDate,
            extendedProps: {
              percentage: assessment.percentage,
              proctored: assessment.proctored,
              assessmentName: assessment.name
            }
          };
          calendarEvents.push(eventObj);
        } else {
          // Add to the draggable elements if not scheduled
          eventsContainer.appendChild(eventEl);
        }
      });
      
      courseCard.appendChild(eventsContainer);
      containerEl.appendChild(courseCard);
    });

    new FullCalendar.Draggable(containerEl, {
      itemSelector: ".fc-event",
      eventData: (eventEl) => ({
        title: eventEl.innerText.trim(),
        backgroundColor: eventEl.dataset.color,
        id: eventEl.dataset.eventId,
        extendedProps: {
          course_code: eventEl.dataset.courseCode,
          percentage: eventEl.dataset.percentage,
          proctored: eventEl.dataset.proctored === "1",
          assessmentName: eventEl.dataset.name
        }
      }),
    });
  }

  function createEventElement(assessment, courseCode, colors) {
    const color = assessment.proctored == 1 ? colors.Proctored : colors.Assignment;
    
    const eventEl = document.createElement("div");
    eventEl.classList.add(
      "fc-event",
      "fc-h-event",
      "fc-daygrid-event",
      "fc-daygrid-block-event"
    );
    eventEl.dataset.color = color;
    eventEl.style.backgroundColor = color;
    eventEl.dataset.eventId = assessment.id;
    eventEl.dataset.courseCode = courseCode;
    eventEl.dataset.percentage = assessment.percentage;
    eventEl.dataset.proctored = assessment.proctored;
    eventEl.dataset.name = assessment.name;
    
    const eventTitle = `${courseCode} - ${assessment.name} (${assessment.percentage}%)`;
    eventEl.innerHTML = '<div class="fc-event-main">' + eventTitle + '</div>';
    
    return eventEl;
  }

  function createEventObject(assessment, colors) {
    // For assessments with explicit scheduled date
    if (assessment.scheduled) {
      return {
        id: assessment.id,
        title: `${assessment.course_code} - ${assessment.name}`,
        backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
        start: assessment.scheduled,
        allDay: true,
        extendedProps: {
          percentage: assessment.percentage,
          proctored: assessment.proctored,
          assessmentName: assessment.name
        }
      };
    }
    
    // For assessments with week/day scheduling
    const startDate = getDateFromWeekDay(semesterStartDate, assessment.start_week, assessment.start_day);
    const endDate = assessment.end_week && assessment.end_day ? 
                    getDateFromWeekDay(semesterStartDate, assessment.end_week, assessment.end_day) : 
                    startDate;
    
    return {
      id: assessment.id,
      title: `${assessment.course_code} - ${assessment.name} (${assessment.percentage}%)`,
      backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
      start: startDate,
      end: endDate,
      allDay: true,
      extendedProps: {
        percentage: assessment.percentage,
        proctored: assessment.proctored,
        assessmentName: assessment.name
      }
    };
  }

  function filterEvents(level, courseCode, type) {
    let filteredEvents = exams;
    
    // Filter by course level if specified
    if (level !== "0") {
      filteredEvents = filteredEvents.filter(item => {
        return item.course_code && item.course_code[4] === level;
      });
    }
    
    // Filter by specific course if specified
    if (courseCode !== "My Courses" && courseCode !== "all") {
      filteredEvents = filteredEvents.filter(item => item.course_code === courseCode);
    } else if (courseCode === "all") {
      filteredEvents = otherExams;
    }
    
    // Filter by assessment type if specified
    if (type !== "all") {
      const isProctored = type === "1";
      filteredEvents = filteredEvents.filter(item => (item.proctored == isProctored));
    }
    
    return filteredEvents;
  }

  function updateCalendarEvents(calendar, newEvents) {
    calendar.removeAllEvents();
    
    const updatedEvents = newEvents.map(assessment => {
      return createEventObject(assessment, colors);
    });
    
    calendar.addEventSource(updatedEvents);
    calendar.refetchEvents();
  }

  function handleEventEdit(info) {
    const event = info.event;
    const data = extractEventDetails(event);
    console.log("Event edited:", data);
    saveEvent(data);
  }

  function handleNewItem(arg) {
    const event = arg.draggedEl;
    const eventId = event.dataset.eventId;
    const courseCode = event.dataset.courseCode;
    const assessmentName = event.dataset.name;
    const percentage = event.dataset.percentage;
    const proctored = event.dataset.proctored;
    
    // Calculate the week and day based on the drop date relative to semester start
    const dropDate = arg.date;
    const timeDiff = dropDate - semesterStartDate;
    const daysDiff = Math.floor(timeDiff / (24 * 60 * 60 * 1000));
    const weekNum = Math.floor(daysDiff / 7) + 1;
    const dayNum = (daysDiff % 7) + 1;
    
    const data = {
      id: eventId,
      course_code: courseCode,
      start_week: weekNum,
      start_day: dayNum,
      end_week: weekNum,
      end_day: dayNum + 1,  // Default to one day duration
      proctored: proctored
    };
    
    console.log("New item dropped:", data);
    saveEvent(data);
    arg.draggedEl.parentNode.removeChild(arg.draggedEl);
  }

  function extractEventDetails(event) {
    const id = event.id;
    const startDate = event.start;
    
    // Calculate the week and day based on the event date relative to semester start
    const timeDiff = startDate - semesterStartDate;
    const daysDiff = Math.floor(timeDiff / (24 * 60 * 60 * 1000));
    const startWeek = Math.floor(daysDiff / 7) + 1;
    const startDay = (daysDiff % 7) + 1;
    
    let endWeek = startWeek;
    let endDay = startDay;
    
    if (event.end) {
      const endTimeDiff = event.end - semesterStartDate;
      const endDaysDiff = Math.floor(endTimeDiff / (24 * 60 * 60 * 1000));
      endWeek = Math.floor(endDaysDiff / 7) + 1;
      endDay = (endDaysDiff % 7) + 1;
    }
    
    return { 
      id, 
      start_week: startWeek,
      start_day: startDay,
      end_week: endWeek,
      end_day: endDay,
      extendedProps: event.extendedProps
    };
  }

  function saveEvent(data) {
    $.ajax({
      url: "/update_assessment_schedule",
      method: "POST",
      data,
      success: () => {
        console.log("Assessment schedule updated successfully");
        location.reload();
      },
      error: (xhr, status, error) => {
        console.error("Error updating assessment schedule:", error);
        alert("Failed to update assessment schedule. Please try again.");
      }
    });
  }
});