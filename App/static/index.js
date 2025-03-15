var weekCounter = 0;

document.addEventListener("DOMContentLoaded", function () {
  // Enhanced debugging
  console.log("Calendar initialization started");
  console.log("Initial scheduled assessments:", scheduledAssessments);
  
  // Update colors to use darker shades for both proctored and regular assessments
  const colors = {
    Assignment: '#3e2a73', // Darker version of tertiary color
    Quiz: "#37705a", // Darker version
    Project: "#004850", // Darker version
    Exam: "#a03e3e", // Darker version
    Presentation: "#a45e38", // Darker version
    Other: "#9a7502", // Darker version
    Pending: "#757575", // Darker version
    Proctored: '#7678b0' // Darker version of the proctored color
  };

  // Function to properly format dates for FullCalendar
  function formatDate(dateStr) {
    if (!dateStr) return null;
    
    // Handle ISO format dates (with T)
    if (typeof dateStr === 'string' && dateStr.includes('T')) {
      return dateStr.split('T')[0]; // Extract just the date part
    }
    
    return dateStr;
  }
  
  // Enhanced logging for debugging
  console.log("Preparing calendar events from scheduled assessments:", scheduledAssessments.length);
  if (scheduledAssessments && scheduledAssessments.length > 0) {
    scheduledAssessments.forEach(assessment => {
      console.log(`Assessment ${assessment.id}: ${assessment.name}, Date: ${assessment.scheduled}, Type: ${typeof assessment.scheduled}`);
    });
  } else {
    console.warn("No scheduled assessments found!");
  }
  
  // Initialize calendar events with scheduled assessments only
  const calendarEvents = (scheduledAssessments || [])
    .filter(assessment => assessment.scheduled !== null && assessment.scheduled !== undefined)
    .map(assessment => {
      // Process the scheduled date
      let startDate = formatDate(assessment.scheduled);
      console.log(`Assessment ID ${assessment.id} mapped to date: ${startDate}`);
      
      if (!startDate) {
        console.warn(`Assessment ID ${assessment.id} has no valid scheduled date:`, assessment.scheduled);
        return null; // Skip assessments without a valid date
      }
      
      return {
        id: assessment.id,
        title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
        start: startDate,
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
    })
    .filter(event => event !== null);

  console.log("Processed calendar events:", calendarEvents.length, calendarEvents);

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
  if (unscheduledList) {
    new FullCalendar.Draggable(unscheduledList, {
      itemSelector: ".draggable-assessment",
      eventData: function(eventEl) {
        return {
          id: eventEl.dataset.assessmentId,
          title: `${eventEl.dataset.courseCode}-${eventEl.dataset.name || eventEl.children[0].innerText.split('-')[1]} (${eventEl.dataset.percentage}%)`,
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
  }

  // Create the calendar
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    headerToolbar: {
      left: "prev,next,today",
      center: "title",
      right: "semesterView,dayGridMonth,timeGridWeek",
    },
    views: {
      semesterView: {
        type: "dayGridMonth",
        duration: { weeks: semesterWeeks },
        buttonText: "Semester",
        visibleRange: semester && semester.start_date && semester.end_date ? {
          start: semester.start_date,
          end: semester.end_date,
        } : null,
      },
    },
    height: 'auto',
    allDaySlot: false,
    slotMinTime: "08:00:00",
    slotMaxTime: "20:00:00",
    editable: true,
    selectable: true,
    droppable: true,
    
    // Enhanced event styling to match draggable items
    eventDidMount: function(info) {
      console.log("Event mounted:", info.event.title, "Date:", info.event.start);
      
      // Apply consistent styling to match draggable cards
      const eventEl = info.el;
      const eventContent = eventEl.querySelector('.fc-event-title');
      
      // Get event properties
      const isProctored = info.event.extendedProps?.proctored;
      const courseCode = info.event.extendedProps?.course_code || '';
      const percentage = info.event.extendedProps?.percentage || '';
      const assessmentName = info.event.extendedProps?.assessmentName || '';
      
      // Create a custom HTML structure similar to draggable cards
      let html = `
        <div class="assessment-name">${courseCode}-${assessmentName}</div>
        <div class="assessment-details">
          Weight: ${percentage}%
          ${isProctored ? '<span class="badge">Proctored</span>' : ''}
        </div>
      `;
      
      // Update the event content
      if (eventContent) {
        eventContent.innerHTML = html;
      }
      
      // Add a left border for proctored events to match the draggable style
      if (isProctored) {
        eventEl.style.borderLeft = '4px solid #9C9FE2';
      } else {
        eventEl.style.borderLeft = '4px solid #fff';
      }
      
      // Add box-shadow and hover effect
      eventEl.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
      eventEl.style.borderRadius = '4px';
      eventEl.style.transition = 'all 0.2s ease';
      
      // Add hover effect
      eventEl.addEventListener('mouseenter', function() {
        eventEl.style.boxShadow = '0 3px 6px rgba(0,0,0,0.3)';
        eventEl.style.transform = 'translateY(-2px)';
      });
      
      eventEl.addEventListener('mouseleave', function() {
        eventEl.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
        eventEl.style.transform = 'translateY(0)';
      });
      
      // Add tooltip with full details
      eventEl.title = info.event.title;
    },
    
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
    }
  });

  // Add the events to the calendar
  if (calendarEvents && calendarEvents.length > 0) {
    console.log("Adding events to calendar:", calendarEvents.length);
    calendarEvents.forEach(event => {
      try {
        calendar.addEvent(event);
        console.log(`Added event ${event.id} to calendar`);
      } catch (e) {
        console.error(`Failed to add event ${event.id}:`, e);
      }
    });
  } else {
    console.warn("No calendar events to add");
  }

  try {
    console.log("Rendering calendar with events:", calendarEvents.length);
    calendar.render();
    
    // Force multiple refreshes to ensure events are displayed
    setTimeout(() => {
      calendar.refetchEvents();
      console.log("Calendar events refreshed (first pass)");
      
      // Second refresh after a delay
      setTimeout(() => {
        calendar.refetchEvents();
        console.log("Calendar events refreshed (second pass)");
      }, 500);
    }, 300);
  } catch (error) {
    console.error('Error rendering calendar:', error);
  }

  // Event handlers for filters
  if (levelFilter) {
    levelFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  if (courseFilter) {
    courseFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  if (typeFilter) {
    typeFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  function filterEvents(level, courseCode, type) {
    let filteredEvents = scheduledAssessments || [];
    
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
    
    const updatedEvents = newEvents
      .filter(assessment => assessment.scheduled !== null && assessment.scheduled !== undefined)
      .map(assessment => {
        // Process the scheduled date
        let startDate = formatDate(assessment.scheduled);
        
        if (!startDate) {
          console.warn(`Assessment ID ${assessment.id} has no valid scheduled date in filter update`);
          return null; // Skip assessments without a valid date
        }
        
        return {
          id: assessment.id,
          title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
          start: startDate,
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
      })
      .filter(event => event !== null);
    
    console.log("Updating calendar with events:", updatedEvents.length);
    
    // Add each event individually
    updatedEvents.forEach(event => {
      calendar.addEvent(event);
    });
    
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
          
          // Update the calendar with the latest scheduled assessments
          calendar.removeAllEvents();
          
          const updatedEvents = scheduledAssessments
            .filter(assessment => assessment.scheduled !== null)
            .map(assessment => {
              // Process the scheduled date
              let startDate = formatDate(assessment.scheduled);
              
              if (!startDate) {
                console.warn(`Assessment ID ${assessment.id} has no valid scheduled date after save`);
                return null; // Skip assessments without a valid date
              }
              
              return {
                id: assessment.id,
                title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
                start: startDate,
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
            })
            .filter(event => event !== null);
          
          console.log("Refreshing calendar with updated events:", updatedEvents.length);
          
          // Add each event individually instead of using addEventSource
          updatedEvents.forEach(event => {
            calendar.addEvent(event);
          });
          
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