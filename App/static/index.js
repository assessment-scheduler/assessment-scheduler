var weekCounter = 0;

document.addEventListener("DOMContentLoaded", function () {
  let eventsLoaded = false;
  
  console.log("Calendar init - Semester dates:", semester);
  if (semester && semester.start_date && semester.end_date) {
    console.log("Start date:", new Date(semester.start_date));
    console.log("End date:", new Date(semester.end_date));
  }
  
  const colors = {
    Assignment: "#4a88c7",
    Quiz: "#4a88c7",
    Project: "#4a88c7",
    Exam: "#4a88c7",
    Presentation: "#4a88c7",
    Other: "#4a88c7",
    Pending: "#999999",
    Proctored: "#674ECC"
  };

  function formatDate(dateStr) {
    if (!dateStr) return null;
    
    console.log("Formatting date:", dateStr, "Type:", typeof dateStr);
    
    try {
      // Handle ISO string format
      if (typeof dateStr === 'string' && dateStr.includes('T')) {
        return dateStr.split('T')[0];
      }
      
      // Handle date object
      if (dateStr instanceof Date) {
        return dateStr.toISOString().split('T')[0];
      }
      
      // Handle string date without T
      if (typeof dateStr === 'string' && dateStr.match(/^\d{4}-\d{2}-\d{2}/)) {
        return dateStr.substring(0, 10);
      }
      
      return dateStr;
    } catch (error) {
      console.error("Error formatting date:", error, dateStr);
      return null;
    }
  }

  const calendarEvents = (scheduledAssessments || [])
    .filter(assessment => assessment.scheduled !== null && assessment.scheduled !== undefined)
    .map(assessment => {
      let startDate = formatDate(assessment.scheduled);
      if (!startDate) return null;
      
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
  const scheduledList = document.getElementById("scheduled-list");

  if (!calendarEl) return;

  if (unscheduledList) {
    console.log("Initializing drag for unscheduled assessments");
    
    // Find all draggable unscheduled items
    const draggableItems = unscheduledList.querySelectorAll('.draggable-assessment.status-unscheduled.can-drag');
    console.log(`Found ${draggableItems.length} draggable unscheduled assessments`);
    
    // More detailed logging to debug draggable elements
    const allItems = unscheduledList.querySelectorAll('.draggable-assessment');
    console.log(`Total items in list: ${allItems.length}`);
    console.log(`Unscheduled items: ${unscheduledList.querySelectorAll('.status-unscheduled').length}`);
    console.log(`Scheduled items: ${unscheduledList.querySelectorAll('.scheduled').length}`);
    
    // Log first few items for debugging
    if (draggableItems.length > 0) {
      console.log("Sample draggable item:", draggableItems[0]);
      console.log("Sample item data:", draggableItems[0].dataset);
    } else {
      console.warn("NO DRAGGABLE ITEMS FOUND - check class names!");
      
      // Fallback to any unscheduled assessment
      const anyUnscheduled = unscheduledList.querySelectorAll('.status-unscheduled');
      if (anyUnscheduled.length > 0) {
        console.log("Found unscheduled items without can-drag class:", anyUnscheduled.length);
        console.log("Sample unscheduled item:", anyUnscheduled[0]);
      }
    }
    
    new FullCalendar.Draggable(unscheduledList, {
      itemSelector: ".draggable-assessment.status-unscheduled",
      eventData: function(eventEl) {
        console.log("Dragging assessment:", eventEl.dataset);
        return {
          id: eventEl.dataset.assessmentId,
          title: `${eventEl.dataset.courseCode}-${eventEl.dataset.name || eventEl.children[0].innerText.split('-')[1]} (${eventEl.dataset.percentage}%)`,
          backgroundColor: eventEl.dataset.proctored === "1" || eventEl.dataset.proctored === "True" || eventEl.dataset.proctored === "true" ? colors.Proctored : colors.Assignment,
          textColor: '#fff',
          extendedProps: {
            course_code: eventEl.dataset.courseCode,
            percentage: eventEl.dataset.percentage,
            proctored: eventEl.dataset.proctored === "1" || eventEl.dataset.proctored === "True" || eventEl.dataset.proctored === "true",
          }
        };
      },
      mirrorSelector: ".draggable-assessment",
      dragRevertDuration: 0,
      droppableScope: 'assessment'
    });
  }

  if (scheduledList) {
    new FullCalendar.Draggable(scheduledList, {
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
      },
      mirrorSelector: ".draggable-assessment",
      dragRevertDuration: 0,
      droppableScope: 'assessment'
    });
  }

  // Add draggable functionality to the expanded assessment list
  const allAssessmentsList = document.getElementById("all-assessments");
  if (allAssessmentsList) {
    console.log("Initializing drag for expanded assessments list");
    new FullCalendar.Draggable(allAssessmentsList, {
      itemSelector: ".draggable-assessment",
      eventData: function(eventEl) {
        console.log("Dragging assessment from expanded list:", eventEl.dataset);
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
      },
      mirrorSelector: ".draggable-assessment",
      dragRevertDuration: 0,
      droppableScope: 'assessment'
    });
  }

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",  // Use standard month view initially
    headerToolbar: {
      left: "prev,next,today",
      center: "title",
      right: "dayGridMonth,timeGridWeek",
    },
    customButtons: {
      fullSemester: {
        text: 'Full Semester',
        click: function() {
          if (semester && semester.start_date && semester.end_date) {
            console.log("Showing full semester range:", semester.start_date, "to", semester.end_date);
            
            const startDate = new Date(semester.start_date);
            const endDate = new Date(semester.end_date);
            
            // Calculate the number of months to display
            const monthDiff = (endDate.getFullYear() - startDate.getFullYear()) * 12 + 
                              (endDate.getMonth() - startDate.getMonth()) + 1;
            
            console.log("Number of months in semester:", monthDiff);
            
            // Use multiMonth view to show all months in the semester
            calendar.setOption('multiMonthMaxColumns', 3); // Adjust based on screen size
            calendar.setOption('multiMonthMinWidth', 250); // Adjust based on preference
            
            calendar.gotoDate(startDate);
            calendar.changeView('multiMonth', {
              duration: { months: monthDiff }
            });
          }
        }
      }
    },
    views: {
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
    dayMaxEvents: 2, // Limit visible events to 2 per day
    
    // Configure the "more" events popover
    moreLinkClick: 'popover',
    eventPopoverDidMount: function(info) {
      // Make the popover content larger and scrollable
      const popoverContent = info.el.querySelector('.fc-popover-body');
      if (popoverContent) {
        popoverContent.style.maxHeight = '300px';
        popoverContent.style.overflowY = 'auto';
        popoverContent.style.padding = '10px';
      }
      
      // Make sure the popover doesn't block dropping
      info.el.addEventListener('mouseenter', function() {
        // Set a short timeout to hide the popover when users are dragging
        const dragStartHandler = function() {
          info.el.style.display = 'none';
          document.removeEventListener('dragstart', dragStartHandler);
        };
        
        document.addEventListener('dragstart', dragStartHandler);
      });
    },
    
    eventStartEditable: true,
    eventDurationEditable: false,
    removable: true,
    droppableScope: 'assessment',
    dragRevertDuration: 0,
    dragScroll: true,
    dropAccept: '.draggable-assessment',
    
    eventAllow: function(dropInfo, draggedEvent) {
      if (!semester || !semester.start_date || !semester.end_date) {
        return false;
      }
      
      const eventDate = dropInfo.start;
      const semesterStart = new Date(semester.start_date);
      const semesterEnd = new Date(semester.end_date);
      
      return eventDate >= semesterStart && eventDate <= semesterEnd;
    },
    
    viewDidMount: function(info) {
      // Only store dayGridMonth and timeGridWeek views in localStorage
      if (info.view.type === 'dayGridMonth' || info.view.type === 'timeGridWeek') {
        localStorage.setItem('calendarViewType', info.view.type);
      }
    },
    
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
          <div class="badge-container">
            ${isProctored ? '<span class="badge proctored">Proctored</span>' : ''}
          </div>
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
      
      if (!isOwnedAssessment) {
        eventEl.style.opacity = '0.6';
        eventEl.style.cursor = 'default';
        eventEl.style.pointerEvents = isOwnedAssessment ? 'auto' : 'none';
      } else {
        // Add tooltip for owned assessments to indicate they can be clicked
        eventEl.title = 'Click to unschedule';
        eventEl.style.cursor = 'pointer';
      }
      
      eventEl.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';
      eventEl.style.borderRadius = '4px';
      eventEl.style.transition = 'all 0.2s ease';
      
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
    eventDrop: handleEventDrop,
    drop: handleNewItem,
    eventReceive: function(info) {
      const tempEvent = info.event;
      
      console.log("Assessment dropped on calendar:", tempEvent);
      console.log("Event properties:", {
        id: tempEvent.id,
        title: tempEvent.title,
        start: tempEvent.start,
        extendedProps: tempEvent.extendedProps
      });
      
      if (!semester || !semester.start_date) {
        console.error('Semester start date not available');
        tempEvent.remove();
        alert("Cannot schedule assessment: No active semester found.");
        return;
      }
      
      const eventDate = tempEvent.start;
      const semesterStart = new Date(semester.start_date);
      const semesterEnd = new Date(semester.end_date);
      
      console.log("Validating date range:", {
        event: eventDate,
        semesterStart: semesterStart,
        semesterEnd: semesterEnd
      });
      
      if (eventDate < semesterStart || eventDate > semesterEnd) {
        tempEvent.remove();
        alert("Cannot schedule assessment: Date is outside the semester range.");
        return;
      }
      
      // Ensure we have a valid assessment ID
      if (!tempEvent.id) {
        console.error('No assessment ID found on dropped event');
        tempEvent.remove();
        alert("Cannot schedule assessment: Missing assessment ID.");
        return;
      }
      
      try {
        const offsets = calculateWeekAndDayOffsets(tempEvent.start, semester.start_date);
        console.log("Calculated offsets:", offsets);
        
        const eventData = {
          id: tempEvent.id,
          assessment_date: tempEvent.start.toISOString().split('T')[0],
          start_week: offsets.startWeek,
          start_day: offsets.startDay,
          end_week: offsets.endWeek,
          end_day: offsets.endDay
        };
        
        console.log("Saving assessment with data:", eventData);
        saveEvent(eventData, tempEvent);
      } catch (error) {
        console.error("Error scheduling assessment:", error);
        tempEvent.remove();
        alert("Failed to schedule assessment. Please try again.");
      }
    },
    eventDragStop: function(info) {
      // Check if the element was dropped outside of a valid calendar area
      const isOutsideCalendar = document.querySelector('.fc-event-dragging') === null;
      const isOwnedAssessment = info.event.extendedProps?.isOwnedAssessment;
      
      if (isOutsideCalendar && isOwnedAssessment) {
        console.log("Assessment dragged outside calendar:", info.event.id);
        const eventId = info.event.id;
        
        if (confirm('Are you sure you want to unschedule this assessment?')) {
          // Remove the event from the calendar
          info.event.remove();
          // Call the unschedule endpoint
          unscheduleEvent(eventId);
        }
      }
    },
    eventRemove: function(info) {
      // Explicit remove actions, not drag-out
      console.log("Event removed:", info.event.id);
    },
    eventLeave: function(info) {
      console.log("Event left calendar:", info.event.id);
    },
    initialDate: semester && semester.start_date ? semester.start_date : undefined,
    eventClick: function(info) {
      const isOwnedAssessment = info.event.extendedProps?.isOwnedAssessment;
      
      if (isOwnedAssessment) {
        if (confirm('Would you like to unschedule this assessment?')) {
          const eventId = info.event.id;
          info.event.remove();
          unscheduleEvent(eventId);
        }
      }
    },
  });

  if (calendarEvents && calendarEvents.length > 0) {
    calendarEvents.forEach(event => {
      try {
        calendar.addEvent(event);
      } catch (e) {
        console.error(`Failed to add event ${event.id}:`, e);
      }
    });
    eventsLoaded = true;
  }

  try {
    console.log("Rendering calendar...");
    calendar.render();
    
    // Go to semester start date if available
    if (semester && semester.start_date) {
      console.log("Setting calendar initial date to semester start date:", semester.start_date);
      calendar.gotoDate(new Date(semester.start_date));
      
      // Set view to dayGridMonth to ensure we see the monthly view first
      calendar.changeView('dayGridMonth');
    }
    
    // Ensure events are loaded by forcing a refetch after a short delay
    setTimeout(() => {
      console.log("Refreshing calendar events...");
      calendar.refetchEvents();
      
      // Highlight all scheduled assessments briefly to draw attention to them
      const calendarEvents = calendar.getEvents();
      console.log(`Calendar has ${calendarEvents.length} events loaded`);
      
      calendarEvents.forEach(event => {
        const eventEl = event.el;
        if (eventEl) {
          eventEl.style.transition = 'all 0.5s ease';
          eventEl.style.boxShadow = '0 0 8px 2px rgba(103, 78, 204, 0.6)';
          
          setTimeout(() => {
            eventEl.style.boxShadow = '';
          }, 1500);
        }
      });
    }, 300);
    
    // Make sure FullCalendar has initialized properly by checking its APIs
    console.log("Calendar API check:", {
      view: calendar.view ? calendar.view.type : "No view",
      date: calendar.getDate() ? calendar.getDate().toISOString() : "No date",
      events: calendar.getEvents().length
    });
    
  } catch (error) {
    console.error('Error rendering calendar:', error);
  }

  function loadSavedFilters() {
    console.log("Loading saved filters from localStorage");
    
    if (levelFilter && localStorage.getItem('calendarLevelFilter')) {
      levelFilter.value = localStorage.getItem('calendarLevelFilter');
      console.log("Loaded level filter:", levelFilter.value);
    }
    
    if (courseFilter && localStorage.getItem('calendarCourseFilter')) {
      const savedCourse = localStorage.getItem('calendarCourseFilter');
      const courseExists = Array.from(courseFilter.options).some(option => option.value === savedCourse);
      
      if (courseExists) {
        courseFilter.value = savedCourse;
        console.log("Loaded course filter:", courseFilter.value);
      } else {
        console.log("Saved course doesn't exist in options:", savedCourse);
      }
    }
    
    if (typeFilter && localStorage.getItem('calendarTypeFilter')) {
      typeFilter.value = localStorage.getItem('calendarTypeFilter');
      console.log("Loaded type filter:", typeFilter.value);
    }
    
    if (levelFilter && courseFilter && typeFilter) {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      
      console.log("Applying saved filters:", { selectedLevel, selectedCourse, selectedType });
      
      if (selectedLevel !== "0" || selectedCourse !== "all" || selectedType !== "all") {
        const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
        console.log("Initial filtered events count:", filteredEvents.length);
        updateCalendarEvents(calendar, filteredEvents, false);
      }
    }
  }

  setTimeout(loadSavedFilters, 300);

  if (levelFilter) {
    levelFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      
      console.log("Level filter changed:", selectedLevel);
      localStorage.setItem('calendarLevelFilter', selectedLevel);
      
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      console.log(`Filtered events by level ${selectedLevel}:`, filteredEvents.length);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  if (courseFilter) {
    courseFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      
      console.log("Course filter changed:", selectedCourse);
      localStorage.setItem('calendarCourseFilter', selectedCourse);
      
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      console.log(`Filtered events by course ${selectedCourse}:`, filteredEvents.length);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  if (typeFilter) {
    typeFilter.addEventListener("change", function () {
      const selectedLevel = levelFilter.value;
      const selectedCourse = courseFilter.value;
      const selectedType = typeFilter.value;
      
      console.log("Type filter changed:", selectedType);
      localStorage.setItem('calendarTypeFilter', selectedType);
      
      const filteredEvents = filterEvents(selectedLevel, selectedCourse, selectedType);
      console.log(`Filtered events by type ${selectedType}:`, filteredEvents.length);
      updateCalendarEvents(calendar, filteredEvents);
    });
  }

  function filterEvents(level, courseCode, type) {
    let filteredEvents = scheduledAssessments || [];
    
    if (level !== "0") {
      filteredEvents = filteredEvents.filter(item => {
        return item.course_code && item.course_code.length >= 5 && item.course_code[4] === level;
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
      // Convert type to boolean or number based on the format in the data
      const isProctored = type === "1";
      filteredEvents = filteredEvents.filter(item => {
        // Handle both boolean and numeric representations of proctored
        if (typeof item.proctored === 'boolean') {
          return item.proctored === isProctored;
        } else {
          return (item.proctored == 1) === isProctored;
        }
      });
    }
    
    return filteredEvents;
  }

  function updateCalendarEvents(calendar, newEvents, removeExisting = true) {
    console.log("Updating calendar with filtered events:", newEvents.length);
    
    if (removeExisting) {
      calendar.removeAllEvents();
      console.log("Removed all existing events from calendar");
    }
    
    const updatedEvents = newEvents
      .filter(assessment => assessment.scheduled !== null && assessment.scheduled !== undefined)
      .map(assessment => {
        let startDate = formatDate(assessment.scheduled);
        if (!startDate) {
          console.log("Assessment has invalid date:", assessment);
          return null;
        }
        
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
    
    console.log("Filtered events for calendar:", updatedEvents.length);
    
    updatedEvents.forEach(event => {
      try {
        const existingEvent = calendar.getEventById(event.id);
        if (!existingEvent) {
          calendar.addEvent(event);
        }
      } catch (error) {
        console.error("Error adding event to calendar:", error, event);
      }
    });
    
    // Ensure events are rendered
    setTimeout(() => {
      calendar.render();
    }, 100);
  }

  function calculateWeekAndDayOffsets(date, semesterStartDate) {
    const assessmentDate = new Date(date);
    const startDate = new Date(semesterStartDate);
    
    const dayDiff = Math.floor((assessmentDate - startDate) / (1000 * 60 * 60 * 24));
    
    const weekOffset = Math.floor(dayDiff / 7) + 1; 
    
    let dayOffset = assessmentDate.getDay();
    if (dayOffset === 0) {
      dayOffset = 7;  
    }
    
    return {
      startWeek: weekOffset,
      startDay: dayOffset,
      endWeek: weekOffset,
      endDay: dayOffset
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

  function handleEventDrop(info) {
    const eventDate = info.event.start;
    const semesterStart = new Date(semester.start_date);
    const semesterEnd = new Date(semester.end_date);
    
    if (eventDate < semesterStart || eventDate > semesterEnd) {
      info.revert();
      alert("Cannot schedule assessment: Date is outside the semester range.");
      return;
    }
    
    handleEventEdit(info);
  }

  function handleNewItem(info) {
    return;
  }

  function saveEvent(data, tempEvent = null) {
    console.log("saveEvent called with data:", data);
    
    const currentLevel = levelFilter ? levelFilter.value : "0";
    const currentCourse = courseFilter ? courseFilter.value : "all";
    const currentType = typeFilter ? typeFilter.value : "all";
    
    if (calendar) {
      localStorage.setItem('calendarViewType', calendar.view.type);
    }

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

    console.log('Sending assessment update:', {
      id: data.id,
      date: data.assessment_date,
      start_week: data.start_week,
      start_day: data.start_day,
      end_week: data.end_week,
      end_day: data.end_day
    });

    try {
      const formattedData = {
        id: parseInt(data.id),
        assessment_date: data.assessment_date,
        start_week: parseInt(data.start_week),
        start_day: parseInt(data.start_day),
        end_week: parseInt(data.end_week),
        end_day: parseInt(data.end_day)
      };
  
      const form = document.createElement('form');
      form.method = 'POST';
      form.action = '/update_assessment_schedule';
      form.style.display = 'none';
      
      for (const key in formattedData) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = key;
        input.value = formattedData[key];
        form.appendChild(input);
      }
      
      document.body.appendChild(form);
      
      // Add visual feedback
      if (tempEvent && tempEvent.el) {
        tempEvent.el.style.boxShadow = '0 0 10px 2px rgba(46, 204, 113, 0.7)';
      }
      
      form.submit();
    } catch (error) {
      console.error("Error submitting form:", error);
      alert("Error scheduling assessment. Please try again.");
      
      if (tempEvent) {
        tempEvent.remove();
      }
    }
  }

  function unscheduleEvent(eventId) {
    if (calendar) {
      localStorage.setItem('calendarViewType', calendar.view.type);
    }
    
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/unschedule_assessment';
    form.style.display = 'none';
    
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'id';
    input.value = eventId;
    form.appendChild(input);
    
    document.body.appendChild(form);
    form.submit();
  }

  const disclaimerText = document.createElement("div");
  disclaimerText.textContent = "Page may occasionally refresh on calendar input";
  disclaimerText.style.color = "#666";
  disclaimerText.style.fontSize = "12px";
  disclaimerText.style.marginBottom = "8px";
  disclaimerText.style.textAlign = "center";
  disclaimerText.style.fontStyle = "italic";

  const filters = document.getElementById("filters");
  if (filters) {
    filters.style.marginBottom = '20px';
    
    const selects = filters.querySelectorAll('select');
    selects.forEach(select => {
      select.style.backgroundColor = 'var(--tertiary-color)';
      select.style.color = 'white';
      select.style.border = '1px solid var(--tertiary-color)';
      select.style.borderRadius = '4px';
      select.style.padding = '8px 12px';
      select.style.margin = '0 8px 8px 0';
      select.style.cursor = 'pointer';
      select.style.fontWeight = '500';
      
      const options = select.querySelectorAll('option');
      options.forEach(option => {
        option.style.backgroundColor = 'var(--tertiary-color)';
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function() {
    const collapsibleHeaders = document.querySelectorAll('.collapsible-header');
    
    collapsibleHeaders.forEach(header => {
      header.addEventListener('click', function() {
        this.classList.toggle('collapsed');
        const content = this.nextElementSibling;
        content.classList.toggle('collapsed');
      });
    });
    
    const showMoreBtn = document.getElementById('show-more-btn');
    const showLessBtn = document.getElementById('show-less-btn');
    const allAssessments = document.getElementById('all-assessments');
    
    if (showMoreBtn) {
      showMoreBtn.addEventListener('click', function() {
        allAssessments.classList.remove('hidden');
        showMoreBtn.style.display = 'none';
        
        // Reinitialize draggable functionality for the now-visible assessments
        setTimeout(() => {
          if (allAssessments) {
            console.log("Reinitializing drag for expanded assessments after show");
            new FullCalendar.Draggable(allAssessments, {
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
              },
              mirrorSelector: ".draggable-assessment",
              dragRevertDuration: 0,
              droppableScope: 'assessment'
            });
          }
        }, 100);
      });
    }
    
    if (showLessBtn) {
      showLessBtn.addEventListener('click', function() {
        allAssessments.classList.add('hidden');
        showMoreBtn.style.display = 'block';
      });
    }
    
    // Add click handler for scheduled assessments in the list
    setTimeout(() => {
      const scheduledAssessmentsInList = document.querySelectorAll('#unscheduled-list .draggable-assessment.scheduled');
      console.log("Found scheduled assessments in list:", scheduledAssessmentsInList.length);
      
      scheduledAssessmentsInList.forEach(assessment => {
        assessment.addEventListener('click', function(e) {
          console.log("Scheduled assessment clicked:", this.dataset);
          if (e.target.closest('.draggable-assessment.scheduled')) {
            const assessmentId = this.dataset.assessmentId;
            const event = calendar.getEventById(assessmentId);
            
            if (event) {
              // Go to the date of the assessment
              calendar.gotoDate(event.start);
              
              // Highlight the event
              const eventEl = event.el;
              if (eventEl) {
                eventEl.style.boxShadow = '0 0 10px 2px rgba(255, 255, 0, 0.7)';
                eventEl.style.zIndex = '1000';
                
                // Remove highlight after 2 seconds
                setTimeout(() => {
                  eventEl.style.boxShadow = '';
                  eventEl.style.zIndex = '';
                }, 2000);
              }
            }
          }
        });
      });
    }, 500);
  });

  function applyBlueBackgroundClass() {
    const assessmentItems = document.querySelectorAll('.assessment-item, .draggable-assessment');
    
    assessmentItems.forEach(item => {
      const style = window.getComputedStyle(item);
      const bgColor = style.backgroundColor;
      
      if (bgColor.includes('rgb(92, 70, 180)') || 
          bgColor.includes('rgb(94, 114, 228)') || 
          bgColor.includes('rgb(52, 152, 219)') ||
          item.style.backgroundColor === 'var(--tertiary-color)' ||
          item.style.backgroundColor === '#5e72e4') {
        item.classList.add('blue-bg');
      } else {
        item.classList.remove('blue-bg');
      }
    });
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    applyBlueBackgroundClass();
    
    setTimeout(applyBlueBackgroundClass, 1000);
  });
  
  document.addEventListener('themeToggled', applyBlueBackgroundClass);

  // Check browser console for errors
  console.log("Draggable elements initialized:", 
    document.querySelectorAll(".draggable-assessment").length);
}); 