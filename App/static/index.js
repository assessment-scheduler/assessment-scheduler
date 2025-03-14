var weekCounter = 0;

document.addEventListener("DOMContentLoaded", function () {
  // Debug logging
  console.log("Initial scheduled assessments:", scheduledAssessments);

  // Update colors to use tertiary color (purple) from CSS variables
  const colors = {
    Assignment: 'var(--tertiary-color)',
    Quiz: "#499373",
    Project: "#006064",
    Exam: "#CC4E4E",
    Presentation: "#cc7a50",
    Other: "#C29203",
    Pending: "#999999",
    Proctored: '#9C9FE2'
  };

  // Initialize calendar events with scheduled assessments only
  const calendarEvents = scheduledAssessments.map(assessment => {
    console.log("Processing assessment for calendar:", assessment);
    return {
      id: assessment.id,
      title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
      start: assessment.scheduled,
      allDay: true,
      backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
      textColor: '#fff',
      extendedProps: {
        course_code: assessment.course_code,
        percentage: assessment.percentage,
        proctored: assessment.proctored,
        assessmentName: assessment.name
      }
    };
  }).filter(event => {
    console.log("Filtered event start date:", event.start);
    return event.start != null;
  });

  console.log("Processed calendar events:", calendarEvents);

  const levelFilter = document.getElementById("level");
  const courseFilter = document.getElementById("courses");
  const typeFilter = document.getElementById("assignmentType");
  const calendarEl = document.getElementById("calendar");
  const unscheduledList = document.getElementById("unscheduled-list");

  if (!calendarEl) {
    console.error('Calendar element not found');
    return;
  }

  // Make unscheduled assessments draggable
  new FullCalendar.Draggable(unscheduledList, {
    itemSelector: ".draggable-assessment",
    eventData: function(eventEl) {
      return {
        id: eventEl.dataset.assessmentId,
        title: `${eventEl.dataset.courseCode}-${eventEl.children[0].innerText.split('-')[1]} (${eventEl.dataset.percentage}%)`,
        backgroundColor: eventEl.dataset.proctored === "1" ? colors.Proctored : colors.Assignment,
        textColor: '#fff',
        extendedProps: {
          course_code: eventEl.dataset.courseCode,
          percentage: eventEl.dataset.percentage,
          proctored: eventEl.dataset.proctored === "1",
        }
      };
    }
  });

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
        visibleRange: semester.start_date && semester.end_date ? {
          start: semester.start_date,
          end: semester.end_date,
        } : null,
      },
    },
    allDaySlot: false,
    slotMinTime: "08:00:00",
    slotMaxTime: "20:00:00",
    editable: true,
    selectable: true,
    droppable: true,
    events: calendarEvents,  // Use only the filtered calendar events
    eventResize: handleEventEdit,
    eventDrop: handleEventEdit,
    drop: handleNewItem,
    eventReceive: function(info) {
      // Keep the temporary event until server confirms
      const tempEvent = info.event;
      
      // Save the event to server
      saveEvent({
        id: tempEvent.id,
        assessment_date: tempEvent.start.toISOString().split('T')[0]
      }, tempEvent);
    },
    eventDidMount: function(info) {
      // Add tooltips to events
      info.el.title = info.event.title;
    }
  });

  try {
    calendar.render();
  } catch (error) {
    console.error('Error rendering calendar:', error);
  }

  // Event handlers for filters
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

  function filterEvents(level, courseCode, type) {
    let filteredEvents = scheduledAssessments;
    
    // Filter by course level if specified
    if (level !== "0") {
      filteredEvents = filteredEvents.filter(item => {
        return item.course_code && item.course_code[4] === level;
      });
    }
    
    // Filter by specific course if specified
    if (courseCode !== "My Courses" && courseCode !== "all") {
      filteredEvents = filteredEvents.filter(item => item.course_code === courseCode);
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
    
    const updatedEvents = newEvents.map(assessment => ({
      id: assessment.id,
      title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
      start: assessment.scheduled ? assessment.scheduled.split('T')[0] : assessment.scheduled,
      allDay: true,
      backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
      textColor: '#fff',
      extendedProps: {
        course_code: assessment.course_code,
        percentage: assessment.percentage,
        proctored: assessment.proctored,
        assessmentName: assessment.name
      }
    })).filter(event => event.start !== null);
    
    calendar.addEventSource(updatedEvents);
    calendar.refetchEvents();
  }

  function handleEventEdit(info) {
    const event = info.event;
    const newDate = event.start;
    
    saveEvent({
      id: event.id,
      assessment_date: newDate.toISOString().split('T')[0]
    });
  }

  function handleNewItem(info) {
    // This is now handled by eventReceive
    return;
  }

  function saveEvent(data, tempEvent = null) {
    console.log("Saving event with data:", data);
    $.ajax({
      url: "/update_assessment_schedule",
      method: "POST",
      data: data,
      success: (response) => {
        console.log("Server response:", response);
        
        if (response.success) {
          // Update the scheduledAssessments array
          const updatedAssessment = response.assessment;
          
          // Remove from unscheduled if it was there
          const unscheduledIndex = unscheduledAssessments.findIndex(a => a.id.toString() === data.id.toString());
          if (unscheduledIndex > -1) {
            unscheduledAssessments.splice(unscheduledIndex, 1);
            
            // Remove the draggable element from the UI
            const draggedEl = document.querySelector(`[data-assessment-id="${data.id}"]`);
            if (draggedEl) {
              draggedEl.remove();
            }
          }
          
          // Update or add to scheduledAssessments
          const scheduledIndex = scheduledAssessments.findIndex(a => a.id.toString() === data.id.toString());
          if (scheduledIndex > -1) {
            scheduledAssessments[scheduledIndex] = updatedAssessment;
          } else {
            scheduledAssessments.push(updatedAssessment);
          }
          
          // Update the calendar
          calendar.removeAllEvents();
          const updatedEvents = scheduledAssessments.map(assessment => ({
            id: assessment.id,
            title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
            start: assessment.scheduled,
            allDay: true,
            backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
            textColor: '#fff',
            extendedProps: {
              course_code: assessment.course_code,
              percentage: assessment.percentage,
              proctored: assessment.proctored,
              assessmentName: assessment.name
            }
          })).filter(event => event.start != null);
          
          calendar.addEventSource(updatedEvents);
          calendar.refetchEvents();
        } else {
          // Handle error
          alert(response.message || "Failed to update assessment schedule");
          if (tempEvent) {
            tempEvent.remove();
          }
        }
      },
      error: (xhr, status, error) => {
        console.error("Error details:", {xhr, status, error});
        alert("Failed to update assessment schedule. Please try again.");
        
        if (tempEvent) {
          tempEvent.remove();
        }
      }
    });
  }
});