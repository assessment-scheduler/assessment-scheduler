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
    Proctored: "#7678b0"
  };

  function formatDate(dateStr) {
    if (!dateStr) return null;
    
    if (typeof dateStr === 'string' && dateStr.includes('T')) {
      return dateStr.split('T')[0];
    }
    
    return dateStr;
  }

  const calendarEvents = (scheduledAssessments || [])
    .filter(assessment => assessment.scheduled !== null && assessment.scheduled !== undefined)
    .map(assessment => {
      let startDate = formatDate(assessment.scheduled);
      if (!startDate) return null;
      
      // Check if the assessment belongs to the logged-in user
      const isOwnedAssessment = staff_exams.some(exam => exam.id === assessment.id) || 
                               (myCourses && myCourses.some(course => course.code === assessment.course_code));
      
      return {
        id: assessment.id,
        title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
        start: startDate,
        allDay: true,
        backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
        textColor: '#fff',
        editable: isOwnedAssessment,
        extendedProps: {
          course_code: assessment.course_code,
          percentage: assessment.percentage,
          proctored: assessment.proctored,
          assessmentName: assessment.name,
          isOwnedAssessment: isOwnedAssessment
        }
      };
    })
    .filter(event => event !== null);

  const levelFilter = document.getElementById("level");
  const courseFilter = document.getElementById("courses");
  const typeFilter = document.getElementById("assignmentType");
  const calendarEl = document.getElementById("calendar");
  const unscheduledList = document.getElementById("unscheduled-list");

  if (!calendarEl) return;

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
      timeGridWeek: {
        allDaySlot: true,
        allDayText: 'Assessments',
        slotMinTime: "08:00:00",
        slotMaxTime: "20:00:00",
      }
    },
    height: 'auto',
    displayEventTime: false,
    allDaySlot: true,
    allDayText: 'Assessments',
    slotMinTime: "08:00:00",
    slotMaxTime: "20:00:00",
    editable: true,
    selectable: true,
    droppable: true,
    dayMaxEvents: false,
    
    eventDidMount: function(info) {
      const eventEl = info.el;
      const eventContent = eventEl.querySelector('.fc-event-title');
      
      const isProctored = info.event.extendedProps?.proctored;
      const courseCode = info.event.extendedProps?.course_code || '';
      const percentage = info.event.extendedProps?.percentage || '';
      const assessmentName = info.event.extendedProps?.assessmentName || '';
      const isOwnedAssessment = info.event.extendedProps?.isOwnedAssessment;
      
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
      
      eventEl.style.margin = '2px 0';
      eventEl.style.padding = '4px 8px';
      eventEl.style.height = 'auto';
      eventEl.style.minHeight = '50px';
      eventEl.style.width = '100%';
      
      if (isProctored) {
        eventEl.style.borderLeft = '4px solid #9C9FE2';
      } else {
        eventEl.style.borderLeft = '4px solid #fff';
      }
      
      // Apply faded style for non-owned assessments
      if (!isOwnedAssessment) {
        eventEl.style.opacity = '0.6';
        eventEl.style.cursor = 'default';
        eventEl.style.pointerEvents = isOwnedAssessment ? 'auto' : 'none';
      }
      
      eventEl.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
      eventEl.style.borderRadius = '4px';
      eventEl.style.transition = 'all 0.2s ease';
      
      // Only add hover effects for owned assessments
      if (isOwnedAssessment) {
        eventEl.addEventListener('mouseenter', function() {
          eventEl.style.boxShadow = '0 3px 6px rgba(0,0,0,0.3)';
          eventEl.style.transform = 'translateY(-2px)';
        });
        
        eventEl.addEventListener('mouseleave', function() {
          eventEl.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
          eventEl.style.transform = 'translateY(0)';
        });
      }
      
      eventEl.title = info.event.title;
    },
    
    eventResize: handleEventEdit,
    eventDrop: handleEventEdit,
    drop: handleNewItem,
    eventReceive: function(info) {
      const tempEvent = info.event;
      
      if (!semester || !semester.start_date) {
        console.error('Semester start date not available');
        return;
      }
      
      const offsets = calculateWeekAndDayOffsets(tempEvent.start, semester.start_date);
      
      saveEvent({
        id: tempEvent.id,
        assessment_date: tempEvent.start.toISOString().split('T')[0],
        start_week: offsets.startWeek,
        start_day: offsets.startDay,
        end_week: offsets.endWeek,
        end_day: offsets.endDay
      }, tempEvent);
    }
  });

  if (calendarEvents && calendarEvents.length > 0) {
    calendarEvents.forEach(event => {
      try {
        calendar.addEvent(event);
      } catch (e) {
        console.error(`Failed to add event ${event.id}:`, e);
      }
    });
  }

  try {
    calendar.render();
    
    // Initial refresh to ensure events are displayed
    setTimeout(() => calendar.refetchEvents(), 300);
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
        if (!startDate) return null;
        
        // Check if the assessment belongs to the logged-in user
        const isOwnedAssessment = staff_exams.some(exam => exam.id === assessment.id) || 
                                 (myCourses && myCourses.some(course => course.code === assessment.course_code));
        
        return {
          id: assessment.id,
          title: `${assessment.course_code}-${assessment.name} (${assessment.percentage}%)`,
          start: startDate,
          allDay: true,
          backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
          textColor: '#fff',
          editable: isOwnedAssessment,
          extendedProps: {
            course_code: assessment.course_code,
            percentage: assessment.percentage,
            proctored: assessment.proctored,
            assessmentName: assessment.name,
            isOwnedAssessment: isOwnedAssessment
          }
        };
      })
      .filter(event => event !== null);
    
    updatedEvents.forEach(event => {
      calendar.addEvent(event);
    });
    
    calendar.refetchEvents();
  }

  function calculateWeekAndDayOffsets(date, semesterStartDate) {
    const assessmentDate = new Date(date);
    const startDate = new Date(semesterStartDate);
    
    // Calculate the difference in days
    const dayDiff = Math.floor((assessmentDate - startDate) / (1000 * 60 * 60 * 24));
    
    // Calculate week offset (0-based)
    const weekOffset = Math.floor(dayDiff / 7);
    
    // Calculate day offset (0-based)
    const dayOffset = assessmentDate.getDay();
    
    return {
      startWeek: weekOffset,
      startDay: dayOffset,
      endWeek: weekOffset,  // Since it's a single day event
      endDay: dayOffset     // Since it's a single day event
    };
  }

  function handleEventEdit(info) {
    const event = info.event;
    const newDate = event.start;
    
    if (!semester || !semester.start_date) {
      console.error('Semester start date not available');
      return;
    }
    
    const offsets = calculateWeekAndDayOffsets(newDate, semester.start_date);
    
    saveEvent({
      id: event.id,
      assessment_date: newDate.toISOString().split('T')[0],
      start_week: offsets.startWeek,
      start_day: offsets.startDay,
      end_week: offsets.endWeek,
      end_day: offsets.endDay
    });
  }

  function handleNewItem(info) {
    return;
  }

  function saveEvent(data, tempEvent = null) {
    // Store current filter values
    const currentLevel = levelFilter.value;
    const currentCourse = courseFilter.value;
    const currentType = typeFilter.value;

    if (!data.assessment_date && tempEvent && tempEvent.start) {
      data.assessment_date = tempEvent.start.toISOString().split('T')[0];
      
      if (semester && semester.start_date) {
        const offsets = calculateWeekAndDayOffsets(tempEvent.start, semester.start_date);
        data.start_week = offsets.startWeek;
        data.start_day = offsets.startDay;
        data.end_week = offsets.endWeek;
        data.end_day = offsets.endDay;
      }
    }

    // Log the data being sent
    console.log('Sending assessment update:', {
      id: data.id,
      date: data.assessment_date,
      start_week: data.start_week,
      start_day: data.start_day,
      end_week: data.end_week,
      end_day: data.end_day
    });

    // Ensure all values are properly formatted as integers
    const formattedData = {
      id: parseInt(data.id),
      assessment_date: data.assessment_date,
      start_week: parseInt(data.start_week),
      start_day: parseInt(data.start_day),
      end_week: parseInt(data.end_week),
      end_day: parseInt(data.end_day)
    };

    $.ajax({
      url: "/update_assessment_schedule",
      method: "POST",
      data: formattedData,
      success: (response) => {
        if (response.success) {
          console.log('Successfully updated assessment:', response.assessment);
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
          
          // Apply the stored filter values and update calendar
          levelFilter.value = currentLevel;
          courseFilter.value = currentCourse;
          typeFilter.value = currentType;
          
          const filteredEvents = filterEvents(currentLevel, currentCourse, currentType);
          updateCalendarEvents(calendar, filteredEvents);
        } else {
          alert(response.message || "Failed to update assessment schedule");
          if (tempEvent) {
            tempEvent.remove();
          } else {
            // Reapply filters even on failure
            const filteredEvents = filterEvents(currentLevel, currentCourse, currentType);
            updateCalendarEvents(calendar, filteredEvents);
          }
        }
      },
      error: (xhr, status, error) => {
        console.error("Error details:", {xhr, status, error});
        alert("Failed to update assessment schedule. Please try again.");
        
        if (tempEvent) {
          tempEvent.remove();
        } else {
          // Reapply filters even on error
          const filteredEvents = filterEvents(currentLevel, currentCourse, currentType);
          updateCalendarEvents(calendar, filteredEvents);
        }
      }
    });
  }

  // Add autoschedule button functionality
  const autoscheduleButton = document.createElement("button");
  autoscheduleButton.textContent = "Autoschedule ALL";
  autoscheduleButton.className = "btn mb-3";
  autoscheduleButton.style.width = "100%";
  autoscheduleButton.style.backgroundColor = "#7678b0";  // Purple color matching proctored events
  autoscheduleButton.style.color = "white";
  autoscheduleButton.style.padding = "12px";  // Make it taller
  autoscheduleButton.style.fontWeight = "bold";
  autoscheduleButton.style.border = "none";
  
  if (unscheduledList) {
    // Create a form for the button
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/autoschedule";
    form.style.width = "100%";
    form.style.marginBottom = "1rem";
    
    // Add the button to the form
    form.appendChild(autoscheduleButton);
    
    // Add the form before the unscheduled list
    unscheduledList.parentNode.insertBefore(form, unscheduledList);
    
    // Handle button click
    form.addEventListener("submit", function(e) {
      e.preventDefault();
      
      const warningMessage = `Warning: This will automatically schedule all unscheduled assessments.

• This process may take several minutes
• The algorithm will attempt to find an optimal schedule
• All existing scheduled dates will be preserved
• The page will refresh when complete

Do you want to continue?`;
      
      if (confirm(warningMessage)) {
        autoscheduleButton.disabled = true;
        autoscheduleButton.textContent = "Scheduling...";
        autoscheduleButton.style.backgroundColor = "#9b9dc7";  // Lighter purple for disabled state
        
        // Submit the form
        this.submit();
        
        // Reset button after 60 seconds if no response (increased from 30 to 60 seconds)
        setTimeout(() => {
          if (autoscheduleButton.disabled) {
            autoscheduleButton.disabled = false;
            autoscheduleButton.textContent = "Autoschedule ALL";
            autoscheduleButton.style.backgroundColor = "#7678b0";
            alert("The scheduling process is still running in the background. Please refresh the page in a few moments to see the results.");
          }
        }, 60000);
      }
    });
  }
}); 