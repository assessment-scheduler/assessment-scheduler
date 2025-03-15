var weekCounter = 0;

document.addEventListener("DOMContentLoaded", function () {
  console.log("Calendar initialization started");
  console.log("Initial scheduled assessments:", scheduledAssessments);
  
  const colors = {
    Assignment: '#3e2a73',  
    Quiz: "#37705a", 
    Project: "#004850", 
    Exam: "#a03e3e", 
    Presentation: "#a45e38", 
    Other: "#9a7502", 
    Pending: "#757575", 
    Proctored: '#7678b0'  
  };

  function formatDate(dateStr) {
    if (!dateStr) return null;
    
    if (typeof dateStr === 'string' && dateStr.includes('T')) {
      return dateStr.split('T')[0];
    }
    
    return dateStr;
  }
  
  console.log("Preparing calendar events from scheduled assessments:", scheduledAssessments.length);
  if (scheduledAssessments && scheduledAssessments.length > 0) {
    scheduledAssessments.forEach(assessment => {
      console.log(`Assessment ${assessment.id}: ${assessment.name}, Date: ${assessment.scheduled}, Type: ${typeof assessment.scheduled}`);
    });
  } else {
    console.warn("No scheduled assessments found!");
  }
  
  const calendarEvents = (scheduledAssessments || [])
    .filter(assessment => assessment.scheduled !== null && assessment.scheduled !== undefined)
    .map(assessment => {
      let startDate = formatDate(assessment.scheduled);
      console.log(`Assessment ID ${assessment.id} mapped to date: ${startDate}`);
      
      if (!startDate) {
        console.warn(`Assessment ID ${assessment.id} has no valid scheduled date:`, assessment.scheduled);
        return null; 
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
    
    eventDidMount: function(info) {
      console.log("Event mounted:", info.event.title, "Date:", info.event.start);
      
      const eventEl = info.el;
      const eventContent = eventEl.querySelector('.fc-event-title');
      
      const isProctored = info.event.extendedProps?.proctored;
      const courseCode = info.event.extendedProps?.course_code || '';
      const percentage = info.event.extendedProps?.percentage || '';
      const assessmentName = info.event.extendedProps?.assessmentName || '';
      
      let html = `
        <div class="assessment-name">${courseCode}-${assessmentName}</div>
        <div class="assessment-details">
          Weight: ${percentage}%
          ${isProctored ? '<span class="badge">Proctored</span>' : ''}
        </div>
      `;
      
      if (eventContent) {
        eventContent.innerHTML = html;
      }
      
      if (isProctored) {
        eventEl.style.borderLeft = '4px solid #9C9FE2';
      } else {
        eventEl.style.borderLeft = '4px solid #fff';
      }
      
      eventEl.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
      eventEl.style.borderRadius = '4px';
      eventEl.style.transition = 'all 0.2s ease';
      
      eventEl.addEventListener('mouseenter', function() {
        eventEl.style.boxShadow = '0 3px 6px rgba(0,0,0,0.3)';
        eventEl.style.transform = 'translateY(-2px)';
      });
      
      eventEl.addEventListener('mouseleave', function() {
        eventEl.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
        eventEl.style.transform = 'translateY(0)';
      });
      
      eventEl.title = info.event.title;
    },
    
    eventResize: handleEventEdit,
    eventDrop: handleEventEdit,
    drop: handleNewItem,
    eventReceive: function(info) {
      const tempEvent = info.event;
      
      saveEvent({
        id: tempEvent.id,
        assessment_date: tempEvent.start.toISOString().split('T')[0]
      }, tempEvent);
    }
  });

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
    
    setTimeout(() => {
      calendar.refetchEvents();
      console.log("Calendar events refreshed (first pass)");
      
      setTimeout(() => {
        calendar.refetchEvents();
        console.log("Calendar events refreshed (second pass)");
      }, 500);
    }, 300);
  } catch (error) {
    console.error('Error rendering calendar:', error);
  }

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
    
    if (level !== "0") {
      filteredEvents = filteredEvents.filter(item => {
        return item.course_code && item.course_code[4] === level;
      });
    }
    
    if (courseCode !== "all") {
      if (courseCode === "My Courses") {
        const myAssessmentIds = staff_exams.map(exam => exam.id.toString());
        filteredEvents = filteredEvents.filter(item => myAssessmentIds.includes(item.id.toString()));
      } else {
        filteredEvents = filteredEvents.filter(item => item.course_code === courseCode);
      }
    }
    
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
        let startDate = formatDate(assessment.scheduled);
        
        if (!startDate) {
          console.warn(`Assessment ID ${assessment.id} has no valid scheduled date in filter update`);
          return null;
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
          const updatedAssessment = response.assessment;
          
          const unscheduledIndex = unscheduledAssessments.findIndex(a => a.id.toString() === data.id.toString());
          if (unscheduledIndex > -1) {
            unscheduledAssessments.splice(unscheduledIndex, 1);
            
            const draggedEl = document.querySelector(`[data-assessment-id="${data.id}"]`);
            if (draggedEl) {
              draggedEl.remove();
            }
          }
          
          const scheduledIndex = scheduledAssessments.findIndex(a => a.id.toString() === data.id.toString());
          if (scheduledIndex > -1) {
            scheduledAssessments[scheduledIndex] = updatedAssessment;
          } else {
            scheduledAssessments.push(updatedAssessment);
          }
          
          calendar.removeAllEvents();
          
          const updatedEvents = scheduledAssessments
            .filter(assessment => assessment.scheduled !== null)
            .map(assessment => {
              let startDate = formatDate(assessment.scheduled);
              
              if (!startDate) {
                console.warn(`Assessment ID ${assessment.id} has no valid scheduled date after save`);
                return null;
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
          
          updatedEvents.forEach(event => {
            calendar.addEvent(event);
          });
          
          calendar.refetchEvents();
        } else {
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