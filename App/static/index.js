var weekCounter = 0;

// Global variables for handling assessment scheduling
let pendingScheduleData = null;
let pendingEvent = null;

document.addEventListener("DOMContentLoaded", function () {
  let eventsLoaded = false;
  
  console.log("Calendar init - Semester dates:", semester);
  if (semester && semester.start_date && semester.end_date) {
    console.log("Start date:", new Date(semester.start_date));
    console.log("End date:", new Date(semester.end_date));
  }
  
  // Debug information: Print all scheduled assessments details
  console.log("============ SCHEDULED ASSESSMENTS DEBUG INFO ============");
  console.log(`Total scheduled assessments: ${scheduledAssessments ? scheduledAssessments.length : 0}`);
  if (scheduledAssessments && scheduledAssessments.length > 0) {
    console.table(scheduledAssessments.map(assessment => ({
      id: assessment.id,
      course: assessment.course_code,
      name: assessment.name,
      date: assessment.scheduled,
      percentage: assessment.percentage,
      proctored: assessment.proctored ? "Yes" : "No",
      week: assessment.start_week,
      day: assessment.start_day
    })));
    
    // Group by course
    const courseGroups = {};
    scheduledAssessments.forEach(assessment => {
      if (!courseGroups[assessment.course_code]) {
        courseGroups[assessment.course_code] = [];
      }
      courseGroups[assessment.course_code].push(assessment);
    });
    
    console.log("Scheduled assessments by course:");
    Object.keys(courseGroups).forEach(courseCode => {
      console.log(`${courseCode}: ${courseGroups[courseCode].length} assessments`);
      console.group(courseCode);
      courseGroups[courseCode].forEach(assessment => {
        console.log(`${assessment.name} - ${assessment.scheduled} - ${assessment.percentage}%${assessment.proctored ? " (Proctored)" : ""}`);
      });
      console.groupEnd();
    });
  } else {
    console.log("No scheduled assessments found.");
  }
  console.log("=======================================================");
  
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
    console.log("Initializing drag for assessments in My Assessments list");
    
    // Find all draggable items (both scheduled and unscheduled)
    const draggableItems = unscheduledList.querySelectorAll('.draggable-assessment.can-drag');
    console.log(`Found ${draggableItems.length} draggable assessments`);
    
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
      
      // Fallback to any assessment
      const anyAssessment = unscheduledList.querySelectorAll('.draggable-assessment');
      if (anyAssessment.length > 0) {
        console.log("Found assessments without can-drag class:", anyAssessment.length);
        console.log("Sample assessment item:", anyAssessment[0]);
      }
    }
    
    // Improved draggable initialization with better feedback
    new FullCalendar.Draggable(unscheduledList, {
      itemSelector: ".draggable-assessment.can-drag",
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
            isRescheduling: eventEl.classList.contains('scheduled'),
            assessmentName: eventEl.dataset.name
          }
        };
      },
      mirrorSelector: ".draggable-assessment",
      dragRevertDuration: 0,
      droppableScope: 'assessment',
      dragClass: 'is-dragging',
      mirrorClass: 'assessment-mirror',
      // Add animation effects and feedback during dragging
      elementDragging: function(el, event) {
        // Highlight valid drop targets on drag start
        document.querySelectorAll('.fc-day').forEach(day => {
          day.classList.add('potential-drop-target');
        });
      },
      elementDragStop: function(el, event) {
        // Remove highlights when dragging stops
        document.querySelectorAll('.fc-day').forEach(day => {
          day.classList.remove('potential-drop-target');
          day.classList.remove('active-drop-target');
        });
      }
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
      droppableScope: 'assessment',
      dragClass: 'is-dragging',
      mirrorClass: 'assessment-mirror',
      elementDragging: function(el, event) {
        // Highlight valid drop targets on drag start
        document.querySelectorAll('.fc-day').forEach(day => {
          day.classList.add('potential-drop-target');
        });
      },
      elementDragStop: function(el, event) {
        // Remove highlights when dragging stops
        document.querySelectorAll('.fc-day').forEach(day => {
          day.classList.remove('potential-drop-target');
          day.classList.remove('active-drop-target');
        });
      }
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
    
    // Improved drop handling for better UX
    dragRevert: true, // Revert drag if not dropped successfully
    dragScroll: true, // Auto-scroll while dragging
    longPressDelay: 150, // Make touch interactions more responsive
    eventLongPressDelay: 150, // Also for events
    
    // Change cursors to indicate draggability
    eventDragStart: function(info) {
      document.body.style.cursor = 'grabbing';
      info.el.style.cursor = 'grabbing';
      
      // Add visual effect for dragging
      info.el.classList.add('being-dragged');
      info.el.style.boxShadow = '0 6px 10px rgba(0,0,0,0.3)';
      info.el.style.transform = 'scale(1.05)';
      
      // Highlight calendar days when dragging starts
      document.querySelectorAll('.fc-day').forEach(day => {
        const dayDate = new Date(day.getAttribute('data-date'));
        if (semester && dayDate) {
          const semesterStart = new Date(semester.start_date);
          const semesterEnd = new Date(semester.end_date);
          if (dayDate >= semesterStart && dayDate <= semesterEnd) {
            day.classList.add('drop-target-highlight');
          }
        }
      });
    },
    
    eventDragStop: function(info) {
      document.body.style.cursor = '';
      info.el.style.cursor = '';
      
      // Remove visual dragging effect
      info.el.classList.remove('being-dragged');
      info.el.style.boxShadow = '';
      info.el.style.transform = '';
      
      // Remove highlights
      document.querySelectorAll('.fc-day').forEach(day => {
        day.classList.remove('drop-target-highlight');
      });
    },
    
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
    
    // Add hover effects for calendar days during drag operations
    dayCellDidMount: function(info) {
      const cell = info.el;
      
      // Add hover listeners for drag preview
      cell.addEventListener('dragenter', function(e) {
        // Check if we're currently dragging an assessment
        if (document.querySelector('.is-dragging') || document.querySelector('.fc-event-dragging')) {
          cell.classList.add('active-drop-target');
          
          // Show a preview of where the assessment would be placed
          const dateStr = cell.getAttribute('data-date');
          if (dateStr) {
            // Create or update preview element
            let preview = cell.querySelector('.drop-preview');
            if (!preview) {
              preview = document.createElement('div');
              preview.className = 'drop-preview';
              preview.innerHTML = '<span>Drop assessment here</span>';
              cell.appendChild(preview);
            }
          }
        }
      });
      
      cell.addEventListener('dragleave', function(e) {
        cell.classList.remove('active-drop-target');
        
        // Remove preview
        const preview = cell.querySelector('.drop-preview');
        if (preview) {
          preview.remove();
        }
      });
      
      cell.addEventListener('dragover', function(e) {
        // Required to allow dropping
        e.preventDefault();
      });
      
      // For touch devices
      cell.addEventListener('touchmove', function(e) {
        const touch = e.touches[0];
        const elementAtTouch = document.elementFromPoint(touch.clientX, touch.clientY);
        
        // If we're over a calendar day
        if (elementAtTouch && elementAtTouch.classList.contains('fc-daygrid-day')) {
          // Remove active state from all days
          document.querySelectorAll('.fc-daygrid-day').forEach(day => {
            day.classList.remove('active-drop-target');
          });
          
          // Add active state to current day
          elementAtTouch.classList.add('active-drop-target');
        }
      });
    },
    
    eventStartEditable: true,
    eventDurationEditable: false,
    removable: true,
    droppableScope: 'assessment',
    dragRevertDuration: 0,
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
      
      // Add delete button for owned assessments
      if (isOwnedAssessment) {
        html += `<button class="delete-assessment-btn" title="Unschedule assessment">&times;</button>`;
      }
      
      if (eventContent) {
        eventContent.innerHTML = html;
      }
      
      // Add event listener for delete button
      const deleteBtn = eventEl.querySelector('.delete-assessment-btn');
      if (deleteBtn) {
        deleteBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          
          // Show confirmation dialog
          showUnscheduleConfirmation(info.event.id, courseCode, assessmentName);
        });
      }
      
      // Use our unified card styling
      eventEl.classList.add('calendar-event');
      
      // Set appropriate border-left color based on proctored status
      if (isProctored) {
        eventEl.style.borderLeftColor = '#9C9FE2';
      } else {
        eventEl.style.borderLeftColor = '#4a88c7';
      }
      
      // Adjust interaction based on ownership
      if (!isOwnedAssessment) {
        eventEl.style.opacity = '0.6';
        eventEl.style.cursor = 'default';
        eventEl.style.pointerEvents = 'none';
      } else {
        eventEl.title = 'Drag to reschedule';
        eventEl.style.cursor = 'pointer';
      }
    },
    
    eventResize: handleEventEdit,
    eventDrop: handleEventDrop,
    drop: handleNewItem,
    eventReceive: function(info) {
      console.log("Event received:", info.event);
      
      // Determine if this is a scheduled assessment being rescheduled
      const isRescheduling = info.event.extendedProps.isRescheduling;
      const assessmentId = info.event.id;
      
      // Create data for the API call
      const data = {
        assessment_id: assessmentId,
        assessment_date: info.event.start ? info.event.start.toISOString().split('T')[0] : null,
      };
      
      if (semester && semester.start_date) {
        const offsets = calculateWeekAndDayOffsets(info.event.start, semester.start_date);
        data.start_week = offsets.startWeek;
        data.start_day = offsets.startDay;
        data.end_week = offsets.endWeek;
        data.end_day = offsets.endDay;
      }
      
      console.log("Saving event with data:", data);
      
      // Add visual indicator that we're processing
      const loadingIndicator = document.createElement('div');
      loadingIndicator.className = 'event-loading';
      loadingIndicator.innerHTML = '<div class="loading-spinner"></div>';
      info.event.setProp('classNames', ['processing-drop']);
      
      // If it's already scheduled, we need to unschedule first then reschedule
      if (isRescheduling) {
        console.log("Rescheduling existing assessment:", assessmentId, "to date:", data.assessment_date);
        
        // We'll save the event directly instead of calling unscheduleEvent first
        saveEvent(data, info.event);
        
        // After successful save, we might want to update the UI
        // This will happen in the saveEvent function
        } else {
        // Regular scheduling of an unscheduled assessment
        saveEvent(data, info.event);
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
      // Only handle the click if it's not on the delete button
      // Button clicks are handled separately
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
    
    // Apply filters on initial load
    setTimeout(() => {
      applyFilters();
    }, 300);
    
    if (semester && semester.start_date) {
      console.log("Setting calendar initial date to semester start date:", semester.start_date);
      
      const currentDate = new Date();
      const semesterStartDate = new Date(semester.start_date);
      const semesterEndDate = new Date(semester.end_date);
      
      const savedDate = localStorage.getItem('calendarCurrentDate');
      const savedView = localStorage.getItem('calendarViewType');
      
      if (savedDate) {
        const savedDateObj = new Date(savedDate);
        if (savedDateObj >= semesterStartDate && savedDateObj <= semesterEndDate) {
        console.log("Restoring calendar to saved date:", savedDate);
          calendar.gotoDate(savedDateObj);
      } else {
          goToSemesterDate(calendar, currentDate, semesterStartDate, semesterEndDate);
        }
      } else {
        goToSemesterDate(calendar, currentDate, semesterStartDate, semesterEndDate);
      }
      
      if (savedView) {
        console.log("Restoring saved view type:", savedView);
        calendar.changeView(savedView);
      } else {
        calendar.changeView('dayGridMonth');
      }
    }
    
    function goToSemesterDate(calendar, currentDate, semesterStartDate, semesterEndDate) {
      if (currentDate >= semesterStartDate && currentDate <= semesterEndDate) {
        console.log("Current date is within semester, showing current month");
        calendar.gotoDate(currentDate);
      } 
      else if (currentDate < semesterStartDate) {
        console.log("Current date is before semester, showing semester start month");
        calendar.gotoDate(semesterStartDate);
      } 
      else {
        console.log("Current date is after semester, showing semester end month");
        calendar.gotoDate(semesterEndDate);
      }
    }
    
    // Apply visual styling to dates outside semester range
    const markDatesOutsideSemester = () => {
      if (semester && semester.start_date && semester.end_date) {
        const semesterStart = new Date(semester.start_date);
        const semesterEnd = new Date(semester.end_date);
        
        // Find all day cells in the calendar
        const dayCells = document.querySelectorAll('.fc-daygrid-day');
        
        dayCells.forEach(dayCell => {
          const dateAttr = dayCell.getAttribute('data-date');
          if (dateAttr) {
            const cellDate = new Date(dateAttr);
            
            // Check if date is outside semester range
            if (cellDate < semesterStart || cellDate > semesterEnd) {
              dayCell.classList.add('outside-semester');
            } else {
              dayCell.classList.remove('outside-semester');
            }
          }
        });
      }
    };
    
    // Initial application of outside-semester styling
    markDatesOutsideSemester();
    
    // Apply styling when month changes
    calendar.on('datesSet', function() {
      markDatesOutsideSemester();
      
      // Save current date and view for state preservation
      localStorage.setItem('calendarCurrentDate', calendar.getDate().toISOString());
      localStorage.setItem('calendarViewType', calendar.view.type);
    });
    
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
    try {
      // Restore saved filter values if available
      const savedLevel = localStorage.getItem('calendarLevelFilter');
      const savedCourse = localStorage.getItem('calendarCourseFilter');
      const savedType = localStorage.getItem('calendarTypeFilter');
      
      if (savedLevel && levelFilter) levelFilter.value = savedLevel;
      if (savedCourse && courseFilter) courseFilter.value = savedCourse;
      if (savedType && typeFilter) typeFilter.value = savedType;
      
      // Apply the saved filters
      applyFilters();
    } catch (error) {
      console.error("Error loading saved filters:", error);
    }
  }

  // Apply filters when changed
  if (levelFilter) levelFilter.addEventListener('change', applyFilters);
  if (courseFilter) courseFilter.addEventListener('change', applyFilters);
  if (typeFilter) typeFilter.addEventListener('change', applyFilters);
  
  // Load saved filters on init
  setTimeout(loadSavedFilters, 200);

  function applyFilters() {
    try {
      const levelValue = levelFilter ? levelFilter.value : "0";
      const courseValue = courseFilter ? courseFilter.value : "all";
      const typeValue = typeFilter ? typeFilter.value : "all";
      
      console.log("Applying filters:", levelValue, courseValue, typeValue);
      
      // Save filter selections to localStorage
      if (levelFilter) localStorage.setItem('calendarLevelFilter', levelValue);
      if (courseFilter) localStorage.setItem('calendarCourseFilter', courseValue);
      if (typeFilter) localStorage.setItem('calendarTypeFilter', typeValue);
      
      // Filter calendar events
      if (calendar) {
        const events = calendar.getEvents();
        events.forEach(event => {
          let visible = true;
          
          // Level filter
          if (levelValue !== "0") {
            const courseCode = event.extendedProps.course_code;
            if (courseCode && courseCode.length >= 5) {
              const courseLevel = courseCode.charAt(4);
              if (courseLevel !== levelValue) {
                visible = false;
              }
            }
          }
          
          // Course filter 
          if (courseValue !== "all") {
            if (courseValue === "My Courses") {
              // Only show events for the logged-in lecturer's courses
              // These assessments can be identified by the isOwnedAssessment property
              if (!event.extendedProps.isOwnedAssessment) {
                visible = false;
              }
            } else if (event.extendedProps.course_code !== courseValue) {
              visible = false;
            }
          }
          
          // Type filter
          if (typeValue !== "all") {
            if ((typeValue === "1" && !event.extendedProps.proctored) || 
                (typeValue === "0" && event.extendedProps.proctored)) {
              visible = false;
            }
          }
          
          // Apply visibility
          if (visible) {
            event.setProp('display', 'auto');
          } else {
            event.setProp('display', 'none');
          }
        });
      }
      
      // Update the unscheduled assessments list based on filters
      const assessmentItems = document.querySelectorAll('#unscheduled-list .draggable-assessment');
      assessmentItems.forEach(item => {
        let visible = true;
        
        // Level filter
        if (levelValue !== "0") {
          const courseCode = item.dataset.courseCode;
          if (courseCode && courseCode.length >= 5) {
            const courseLevel = courseCode.charAt(4);
            if (courseLevel !== levelValue) {
              visible = false;
            }
          }
        }
        
        // Course filter - Note: All items in #unscheduled-list are already filtered to the user's courses
        if (courseValue !== "all" && courseValue !== "My Courses") {
          if (item.dataset.courseCode !== courseValue) {
            visible = false;
          }
        }
        
        // Type filter
        if (typeValue !== "all") {
          const isProctored = item.dataset.proctored === "1" || 
                             item.dataset.proctored === "True" || 
                             item.dataset.proctored === "true";
          if ((typeValue === "1" && !isProctored) || (typeValue === "0" && isProctored)) {
            visible = false;
          }
        }
        
        // Apply visibility
        item.style.display = visible ? 'block' : 'none';
      });
    } catch (error) {
      console.error("Error applying filters:", error);
    }
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
    const event = info.event;
    const newDate = event.start;
    
    if (!semester || !semester.start_date || !semester.end_date) {
      info.revert();
      console.error('Semester date range not available');
      alert("Cannot reschedule assessment: No active semester found.");
      return;
    }
    
    const eventDate = newDate;
    const semesterStart = new Date(semester.start_date);
    const semesterEnd = new Date(semester.end_date);
    
    // Validate the drop is within the semester
    if (eventDate < semesterStart || eventDate > semesterEnd) {
      info.revert();
      alert("Cannot reschedule assessment: Date is outside the semester range.");
      return;
    }
    
    console.log("Rescheduling event via drag:", event.id, "to", newDate.toISOString().split('T')[0]);
    
    // Store the original event data and element info for possible recovery
    const originalAssessmentId = event.id;
    const originalElement = document.querySelector(`.draggable-assessment[data-assessment-id="${originalAssessmentId}"]`);
    
    // Save original assessment card details if available
    if (originalElement) {
      window._lastDraggedAssessment = {
        id: originalAssessmentId,
        courseCode: originalElement.dataset.courseCode,
        name: originalElement.dataset.name,
        percentage: originalElement.dataset.percentage,
        proctored: originalElement.dataset.proctored,
        html: originalElement.outerHTML
      };
      console.log("Stored original assessment data:", window._lastDraggedAssessment);
    }
    
    // Calculate week and day offsets
    const offsets = calculateWeekAndDayOffsets(newDate, semester.start_date);
    
    // Create data for saving
    const data = {
      assessment_id: event.id,
      assessment_date: newDate.toISOString().split('T')[0],
      start_week: offsets.startWeek,
      start_day: offsets.startDay,
      end_week: offsets.endWeek,
      end_day: offsets.endDay,
      is_rescheduling: true
    };
    
    // Add visual indicator that we're processing
    event.setProp('classNames', ['processing-drop']);
    
    // Store the original event reference in case we need to revert
    const originalEvent = event;
    
    // Save the event - treat this as a rescheduling
    saveEvent(data, event);
  }

  function handleNewItem(info) {
    return;
  }

  function saveEvent(data, event) {
    // Store the pending schedule data and event
    pendingScheduleData = data;
    pendingEvent = event;
    
    // Keep track of the source element for better recovery
    if (!window._lastDraggedAssessment) {
      window._lastDraggedAssessment = {
        id: data.assessment_id || data.id,
        inProgress: true
      };
    }
    
    // First evaluate the clash value for this assessment date
    evaluateAssessmentClash(data.assessment_id || data.id, data.assessment_date);
  }

  function evaluateAssessmentClash(assessmentId, date) {
    // Show loading state
    document.body.classList.add('loading');
    
    fetch('/evaluate_assessment_date', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        assessment_id: assessmentId,
        date: date
      })
    })
    .then(response => response.json())
    .then(data => {
      document.body.classList.remove('loading');
      
      if (data.success) {
        displayClashEvaluation(data.evaluation);
      } else {
        // If error, just proceed with scheduling
        console.error('Failed to evaluate clash:', data.error);
        commitScheduleEvent();
      }
    })
    .catch(error => {
      document.body.classList.remove('loading');
      console.error('Error evaluating clash:', error);
      // On error, proceed with scheduling
      commitScheduleEvent();
    });
  }

  function displayClashEvaluation(data) {
    const clashValue = document.getElementById('avg-clash-value');
    const clashEvaluation = document.getElementById('clash-evaluation');
    const clashDetailsList = document.getElementById('clash-details-list');
    const highestClashValue = document.getElementById('highest-clash-value');
    
    // First, stop any pending redirect or action that might be in progress
    if (window.redirectInProgress) {
      clearTimeout(window.redirectInProgress);
      window.redirectInProgress = null;
    }
    
    // Set the average clash value with color coding
    if (data.average_clash_value !== undefined) {
      clashValue.textContent = Number(data.average_clash_value).toFixed(1);
      
      if (parseFloat(data.average_clash_value) <= 2.0) {
        clashValue.style.color = '#4cd964'; // green
      } else if (parseFloat(data.average_clash_value) <= 5.0) {
        clashValue.style.color = '#5e72e4'; // blue
      } else {
        clashValue.style.color = '#ff3b30'; // red
      }
    } else {
      clashValue.textContent = "0";
      clashValue.style.color = '#4cd964'; // green
    }
    
    // Set the highest clash value with color coding
    if (data.highest_clash_value !== undefined) {
      highestClashValue.textContent = Number(data.highest_clash_value).toFixed(1);
      
      if (parseFloat(data.highest_clash_value) <= 2.0) {
        highestClashValue.style.color = '#4cd964'; // green
      } else if (parseFloat(data.highest_clash_value) <= 5.0) {
        highestClashValue.style.color = '#5e72e4'; // blue
      } else {
        highestClashValue.style.color = '#ff3b30'; // red
      }
    } else {
      highestClashValue.textContent = "0";
      highestClashValue.style.color = '#4cd964'; // green
    }
    
    // Set the evaluation badge and class
    clashEvaluation.textContent = data.evaluation;
    clashEvaluation.className = 'evaluation-badge ' + data.evaluation.toLowerCase();
    
    // Clear and populate the details list
    clashDetailsList.innerHTML = '';
    
    if (data.details && data.details.length > 0) {
      data.details.forEach(detail => {
        const detailItem = document.createElement('div');
        detailItem.className = 'clash-details-item';
        
        // Format day impact based on the day_factor
        let dayImpact = '';
        if (detail.day_factor >= 1.0) {
          dayImpact = 'High impact (' + detail.days_difference + ' days difference)';
        } else if (detail.day_factor >= 0.6) {
          dayImpact = 'Medium impact (' + detail.days_difference + ' days difference)';
        } else if (detail.day_factor >= 0.3) {
          dayImpact = 'Low impact (' + detail.days_difference + ' days difference)';
        } else {
          dayImpact = 'Minimal impact (' + detail.days_difference + ' days difference)';
        }
        
        const assessmentDate = new Date(detail.assessment_date);
        const formattedDate = assessmentDate.toLocaleDateString();
        
        // Add proctored badge if assessment is proctored
        const proctoredBadge = detail.is_proctored ? 
          '<span class="badge proctored" style="margin-left: 10px;">Proctored</span>' : '';
        
        detailItem.innerHTML = `
          <div class="clash-course-info">
            <span class="clash-course-code">${detail.course_code}</span>
            <span class="clash-overlap">${detail.overlap_count} students overlap</span>
          </div>
          <div class="clash-assessment-info">
            <span class="clash-assessment-name">${detail.assessment_name}${proctoredBadge}</span>
            <span class="clash-assessment-date">${formattedDate}</span>
          </div>
          <div class="clash-contribution">
            <div class="clash-contrib-label">
              <span>${dayImpact}</span>
              <span class="clash-contrib-value">${Number(detail.clash_value).toFixed(1)} clash contribution</span>
            </div>
          </div>
        `;
        clashDetailsList.appendChild(detailItem);
      });
    } else {
      clashDetailsList.innerHTML = '<p>No overlapping assessments found.</p>';
    }
    
    // Show the modal and overlay with proper z-index
    const modal = document.getElementById('clash-modal');
    const overlay = document.getElementById('clash-modal-overlay');
    
    // Apply dark mode styling if needed
    if (isDarkModeActive()) {
      modal.classList.add('dark-mode');
      overlay.classList.add('dark-mode');
    } else {
      modal.classList.remove('dark-mode');
      overlay.classList.remove('dark-mode');
    }
    
    // Ensure the modal has high z-index to stay on top
    modal.style.zIndex = "2000";
    overlay.style.zIndex = "1999";
    
    modal.classList.remove('hidden');
    overlay.style.display = 'block';
    
    // Clear any existing event listeners
    const confirmBtn = document.getElementById('confirm-schedule-btn');
    const cancelBtn = document.getElementById('cancel-schedule-btn');
    const closeBtn = document.getElementById('close-clash-modal');
    
    // Remove old event listeners by cloning and replacing
    const newConfirmBtn = confirmBtn.cloneNode(true);
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    newConfirmBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      // Close modal first
      document.getElementById('clash-modal').classList.add('hidden');
      document.getElementById('clash-modal-overlay').style.display = 'none';
      
      // Wait a moment to ensure UI updates before committing
      setTimeout(() => {
        commitScheduleEvent();
      }, 50);
      
      return false;
    });
    
    const newCancelBtn = cancelBtn.cloneNode(true);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    newCancelBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      document.getElementById('clash-modal').classList.add('hidden');
      document.getElementById('clash-modal-overlay').style.display = 'none';
      
      // Refresh the page when cancel is clicked
      window.location.reload();
      return false;
    });
    
    const newCloseBtn = closeBtn.cloneNode(true);
    closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
    newCloseBtn.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      document.getElementById('clash-modal').classList.add('hidden');
      document.getElementById('clash-modal-overlay').style.display = 'none';
      
      // Refresh the page when close button is clicked
      window.location.reload();
      return false;
    });
    
    // Prevent clicks on the overlay from bubbling
    overlay.onclick = function(e) {
      e.preventDefault();
      e.stopPropagation();
      
      document.getElementById('clash-modal').classList.add('hidden');
      document.getElementById('clash-modal-overlay').style.display = 'none';
      
      // Refresh the page when overlay is clicked
      window.location.reload();
      return false;
    };
  }

  function closeClashModal() {
    const modal = document.getElementById('clash-modal');
    const overlay = document.getElementById('clash-modal-overlay');
    
    console.log("Closing clash modal, will refresh the page");
    
    // Hide the modal first
    modal.classList.add('hidden');
    overlay.style.display = 'none';
    
    // Refresh the page instead of cancelling the event
    window.location.reload();
  }

  function cancelScheduleEvent() {
    console.log("=== CANCEL SCHEDULE EVENT STARTED ===");
    console.log("Pending event:", pendingEvent);
    console.log("Pending data:", pendingScheduleData);
    
    let assessmentId = null;
    let courseCode = null;
    let assessmentName = null;
    
    // PRIORITY: Use stored last dragged assessment if available
    if (window._lastDraggedAssessment && window._lastDraggedAssessment.id) {
      console.log("Using stored last dragged assessment:", window._lastDraggedAssessment);
      assessmentId = window._lastDraggedAssessment.id;
      courseCode = window._lastDraggedAssessment.courseCode;
      assessmentName = window._lastDraggedAssessment.name;
    } 
    // Otherwise extract from pendingEvent or pendingScheduleData
    else if (pendingEvent) {
      try {
        assessmentId = pendingEvent.id || pendingEvent.extendedProps?.id;
        courseCode = pendingEvent.extendedProps?.course_code;
        assessmentName = pendingEvent.extendedProps?.assessmentName;
      } catch (e) {
        console.error("Error extracting event data:", e);
      }
    } else if (pendingScheduleData) {
      assessmentId = pendingScheduleData.assessment_id || pendingScheduleData.id;
    }
    
    console.log("Assessment for recovery - ID:", assessmentId, "Course:", courseCode, "Name:", assessmentName);
    
    // STEP 1: Try to revert the event in the calendar
    let revertSuccess = false;
    try {
      if (pendingEvent && typeof pendingEvent.revert === 'function') {
        console.log("Attempting to revert event in calendar");
        pendingEvent.revert();
        revertSuccess = true;
        console.log("Event reverted successfully");
      } else if (pendingEvent && typeof pendingEvent.remove === 'function') {
        console.log("No revert function, removing event from calendar");
        pendingEvent.remove();
      }
    } catch (error) {
      console.error("Error handling event in calendar:", error);
      
      // If the revert/remove fails, try to force refresh the calendar
      try {
        calendar.refetchEvents();
        console.log("Forced calendar refresh after failed revert");
      } catch (refreshError) {
        console.error("Error refreshing calendar:", refreshError);
      }
    }
    
    // STEP 2: Force manual restoration of the original element if we have it
    if (window._lastDraggedAssessment && window._lastDraggedAssessment.html) {
      // Only do this if the original element is no longer in the DOM
      if (!isAssessmentCardVisible(assessmentId)) {
        console.log("Restoring assessment card from saved HTML");
        
        const unscheduledList = document.getElementById('unscheduled-list');
        if (unscheduledList) {
          // Create a temporary container for the HTML
          const temp = document.createElement('div');
          temp.innerHTML = window._lastDraggedAssessment.html;
          
          // Get the assessment element
          const savedEl = temp.firstChild;
          
          // Ensure it has the recovered class
          savedEl.classList.add('recovered');
          
          // Add it back to the unscheduled list
          const heading = unscheduledList.querySelector('h3');
          if (heading && heading.nextSibling) {
            unscheduledList.insertBefore(savedEl, heading.nextSibling);
          } else {
            unscheduledList.appendChild(savedEl);
          }
          
          // Make it draggable
          new FullCalendar.Draggable(savedEl, {
            eventData: function() {
              return {
                id: savedEl.dataset.assessmentId,
                title: `${savedEl.dataset.courseCode}-${savedEl.dataset.name} (${savedEl.dataset.percentage}%)`,
                backgroundColor: savedEl.dataset.proctored === "1" || savedEl.dataset.proctored === "true" ? colors.Proctored : colors.Assignment,
                textColor: '#fff',
                extendedProps: {
                  course_code: savedEl.dataset.courseCode,
                  percentage: savedEl.dataset.percentage,
                  proctored: savedEl.dataset.proctored,
                  assessmentName: savedEl.dataset.name
                }
              };
            }
          });
          
          console.log("Assessment restored from saved HTML");
        }
      }
    }
    
    // STEP 3: Check if the assessment card is visible in the unscheduled list
    const recoveryNeeded = assessmentId && !isAssessmentCardVisible(assessmentId);
    console.log("Recovery needed after HTML restore check:", recoveryNeeded);
    
    if (recoveryNeeded) {
      console.log("Assessment card not found in DOM, attempting recovery via API");
      
      // STEP 4: Force regeneration of the assessment list via API
      const loadingIndicator = document.createElement('div');
      loadingIndicator.className = 'loading-indicator' + (isDarkModeActive() ? ' dark-mode' : '');
      loadingIndicator.innerHTML = '<div class="spinner"></div><div class="loading-text">Recovering assessment...</div>';
      document.body.appendChild(loadingIndicator);
      
      fetch('/api/my_semester_assessments')
        .then(response => {
          if (!response.ok) {
            throw new Error(`Server returned ${response.status}: ${response.statusText}`);
          }
          return response.json();
        })
        .then(data => {
          if (data.success) {
            console.log("Successfully fetched assessments for recovery");
            
            // Make sure the assessment we're looking for is in the list
            const foundAssessment = data.assessments.find(a => a.id == assessmentId);
            
            if (foundAssessment) {
              console.log("Found assessment in API response:", foundAssessment);
              
              // Generate just the missing card manually if needed
              if (!isAssessmentCardVisible(assessmentId)) {
                manuallyAddAssessmentCard(foundAssessment);
              }
            } else {
              console.warn("Assessment not found in API response, using fallback");
              createFallbackAssessmentCard(assessmentId, courseCode, assessmentName);
            }
            
            // Also update the full list in background
            updateAssessmentList(data.assessments);
          } else {
            console.error("API error:", data.message);
            createFallbackAssessmentCard(assessmentId, courseCode, assessmentName);
          }
        })
        .catch(error => {
          console.error("Error refreshing assessments:", error);
          createFallbackAssessmentCard(assessmentId, courseCode, assessmentName);
        })
        .finally(() => {
          // Remove loading indicator
          if (loadingIndicator.parentNode) {
            loadingIndicator.parentNode.removeChild(loadingIndicator);
          }
          
          // Make sure we apply filters after recovery
          setTimeout(applyFilters, 300);
          
          // Ensure any restored card is visible
          if (assessmentId) {
            const restoredCard = document.querySelector(`.draggable-assessment[data-assessment-id="${assessmentId}"]`);
            if (restoredCard) {
              restoredCard.style.display = 'block';
              // Scroll to the card
              restoredCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            }
          }
        });
    } else {
      console.log("Assessment card already visible, no API recovery needed");
      // Make sure the card is visible
      if (assessmentId) {
        const visibleCard = document.querySelector(`.draggable-assessment[data-assessment-id="${assessmentId}"]`);
        if (visibleCard) {
          visibleCard.style.display = 'block';
          // Highlight the card
          visibleCard.classList.add('recovered');
        }
      }
    }
    
    // STEP 5: Show cancel feedback briefly
    const cancelIndicator = document.createElement('div');
    cancelIndicator.className = 'schedule-feedback cancel';
    cancelIndicator.innerHTML = '<i class="fas fa-times-circle"></i> Scheduling cancelled';
    document.body.appendChild(cancelIndicator);
    
    setTimeout(() => {
      if (cancelIndicator.parentNode) {
        cancelIndicator.parentNode.removeChild(cancelIndicator);
      }
    }, 3000);
    
    // STEP 6: Reset all pending state
    pendingScheduleData = null;
    pendingEvent = null;
    window._lastDraggedAssessment = null;
    
    console.log("=== CANCEL SCHEDULE EVENT COMPLETED ===");
  }
  
  // Helper function to check if an assessment card is visible in the DOM
  function isAssessmentCardVisible(assessmentId) {
    const card = document.querySelector(`.draggable-assessment[data-assessment-id="${assessmentId}"]`);
    return card !== null && getComputedStyle(card).display !== 'none';
  }
  
  // Helper function to create a fallback assessment card when API fails
  function createFallbackAssessmentCard(assessmentId, courseCode, assessmentName) {
    if (!assessmentId) return;
    
    console.log("Creating fallback assessment card:", assessmentId, courseCode, assessmentName);
    
    // Default values if information is missing
    courseCode = courseCode || 'UNKNOWN';
    assessmentName = assessmentName || 'Assessment';
    
    const unscheduledList = document.getElementById('unscheduled-list');
    if (!unscheduledList) return;
    
    // Check if card already exists
    if (isAssessmentCardVisible(assessmentId)) {
      console.log("Card already exists, not creating fallback");
      return;
    }
    
    // Create a new card element
    const assessmentEl = document.createElement('div');
    assessmentEl.className = 'draggable-assessment status-unscheduled can-drag recovered';
    assessmentEl.dataset.assessmentId = assessmentId;
    assessmentEl.dataset.courseCode = courseCode;
    assessmentEl.dataset.name = assessmentName;
    assessmentEl.dataset.scheduled = 'false';
    
    assessmentEl.innerHTML = `
      <span class="assessment-name">${courseCode}-${assessmentName}</span>
      <div class="assessment-details">
        <div class="badge-container">
          <span class="status-badge unscheduled">Unscheduled</span>
          <span class="badge recovered">Recovered</span>
        </div>
      </div>
    `;
    
    // Add after heading but before instructions
    const heading = unscheduledList.querySelector('h3');
    if (heading && heading.nextSibling) {
      unscheduledList.insertBefore(assessmentEl, heading.nextSibling);
    } else {
      unscheduledList.appendChild(assessmentEl);
    }
    
    // Make it draggable
    new FullCalendar.Draggable(assessmentEl, {
      eventData: function() {
        return {
          id: assessmentId,
          title: `${courseCode}-${assessmentName}`,
          backgroundColor: colors.Assignment,
          textColor: '#fff',
          extendedProps: {
            course_code: courseCode,
            assessmentName: assessmentName,
            isRescheduling: false
          }
        };
      }
    });
    
    console.log("Fallback card created successfully");
  }
  
  // Helper function to manually add a specific assessment card
  function manuallyAddAssessmentCard(assessment) {
    if (!assessment || !assessment.id) return;
    
    console.log("Manually adding assessment card:", assessment);
    
    const unscheduledList = document.getElementById('unscheduled-list');
    if (!unscheduledList) return;
    
    // Check if card already exists
    if (isAssessmentCardVisible(assessment.id)) {
      console.log("Card already exists, not adding manually");
      return;
    }
    
    // Create assessment element
    const isScheduled = assessment.scheduled !== null;
    const assessmentEl = document.createElement('div');
    assessmentEl.className = `draggable-assessment ${assessment.proctored ? 'proctored' : ''} ${isScheduled ? 'scheduled' : 'status-unscheduled'} can-drag recovered`;
    assessmentEl.dataset.assessmentId = assessment.id;
    assessmentEl.dataset.courseCode = assessment.course_code;
    assessmentEl.dataset.percentage = assessment.percentage || '';
    assessmentEl.dataset.proctored = assessment.proctored || false;
    assessmentEl.dataset.scheduled = isScheduled ? assessment.scheduled : 'false';
    assessmentEl.dataset.name = assessment.name;
    
    assessmentEl.innerHTML = `
      <span class="assessment-name">${assessment.course_code}-${assessment.name}</span>
      <div class="assessment-details">
        Weight: ${assessment.percentage || ''}%
        <div class="badge-container">
          ${isScheduled ? '<span class="status-badge scheduled">Scheduled</span>' : '<span class="status-badge unscheduled">Unscheduled</span>'}
          ${assessment.proctored ? '<span class="badge proctored">Proctored</span>' : ''}
          <span class="badge recovered">Recovered</span>
        </div>
        ${isScheduled ? `<div>Date: ${assessment.scheduled}</div>` : ''}
      </div>
    `;
    
    // Add after heading but before instructions
    const heading = unscheduledList.querySelector('h3');
    if (heading && heading.nextSibling) {
      unscheduledList.insertBefore(assessmentEl, heading.nextSibling);
    } else {
      unscheduledList.appendChild(assessmentEl);
    }
    
    // Make it draggable
    new FullCalendar.Draggable(assessmentEl, {
      eventData: function() {
        return {
          id: assessment.id,
          title: `${assessment.course_code}-${assessment.name} (${assessment.percentage || ''}%)`,
          backgroundColor: assessment.proctored ? colors.Proctored : colors.Assignment,
          textColor: '#fff',
          extendedProps: {
            course_code: assessment.course_code,
            percentage: assessment.percentage,
            proctored: assessment.proctored,
            isRescheduling: isScheduled,
            assessmentName: assessment.name
          }
        };
      }
    });
    
    console.log("Card manually added successfully");
  }

  function commitScheduleEvent() {
    if (pendingScheduleData) {
      const successIndicator = document.createElement('div');
      successIndicator.className = 'schedule-feedback success';
      successIndicator.innerHTML = '<i class="fas fa-check-circle"></i> Scheduling...';
      document.body.appendChild(successIndicator);
      
      fetch('/schedule_assessment_api', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(pendingScheduleData)
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Update the indicator to show success
          successIndicator.innerHTML = '<i class="fas fa-check-circle"></i> Scheduled successfully';
          successIndicator.className = 'schedule-feedback success';
          
          // Reset pending data
          pendingScheduleData = null;
          pendingEvent = null;
          
          // Redirect with success parameter to refresh page and show flash message
          window.location.href = window.location.pathname + '?scheduled=success';
        } else {
          // Update the indicator to show error
          successIndicator.innerHTML = '<i class="fas fa-exclamation-circle"></i> ' + (data.message || 'Error scheduling');
          successIndicator.className = 'schedule-feedback error';
          
          // Remove the feedback after delay
          setTimeout(() => {
            if (successIndicator.parentNode) {
              successIndicator.parentNode.removeChild(successIndicator);
            }
          }, 3000);
          
          // Refresh UI to restore previous state
          cancelScheduleEvent();
        }
      })
      .catch(error => {
        console.error('Error scheduling assessment:', error);
        
        // Update the indicator to show error
        successIndicator.innerHTML = '<i class="fas fa-exclamation-circle"></i> Network error';
        successIndicator.className = 'schedule-feedback error';
        
        // Remove the feedback after delay
        setTimeout(() => {
          if (successIndicator.parentNode) {
            successIndicator.parentNode.removeChild(successIndicator);
          }
        }, 3000);
        
        // Refresh UI to restore previous state
        cancelScheduleEvent();
      });
    }
  }

  function unscheduleEvent(eventId) {
    if (calendar) {
      localStorage.setItem('calendarViewType', calendar.view.type);
      localStorage.setItem('calendarCurrentDate', calendar.getDate().toISOString());
      
      const currentLevel = levelFilter ? levelFilter.value : "0";
      const currentCourse = courseFilter ? courseFilter.value : "all";
      const currentType = typeFilter ? typeFilter.value : "all";
      
      localStorage.setItem('calendarLevelFilter', currentLevel);
      localStorage.setItem('calendarCourseFilter', currentCourse);
      localStorage.setItem('calendarTypeFilter', currentType);
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
    const closePopupBtn = document.getElementById('close-popup-btn');
    const allAssessments = document.getElementById('all-assessments');
    const popupOverlay = document.querySelector('.popup-overlay');
    
    if (showMoreBtn) {
      showMoreBtn.addEventListener('click', function() {
        allAssessments.classList.remove('hidden');
        popupOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling behind popup
        
        // Ensure close button is attached after popup is opened
        attachCloseButtonHandler();
      });
    }
    
    // Initial attachment of close button handler
    attachCloseButtonHandler();
    
    if (popupOverlay) {
      popupOverlay.addEventListener('click', function() {
        closeAllAssessmentsPopup();
      });
    }
    
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && allAssessments && !allAssessments.classList.contains('hidden')) {
        closeAllAssessmentsPopup();
      }
    });
    
    // Function to close the all assessments popup
    function closeAllAssessmentsPopup() {
      if (allAssessments) {
        allAssessments.classList.add('hidden');
        if (popupOverlay) popupOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
      }
    }
    
    // Function to ensure the close button handler is attached
    function attachCloseButtonHandler() {
      const closeBtn = document.getElementById('close-popup-btn');
      if (closeBtn) {
        // Clone and replace to remove any existing handlers
        const newCloseBtn = closeBtn.cloneNode(true);
        closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
        
        // Add the click handler
        newCloseBtn.addEventListener('click', function(e) {
          e.preventDefault();
          e.stopPropagation();
          closeAllAssessmentsPopup();
        });
      }
    }
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

  // Function to show the unschedule confirmation dialog
  function showUnscheduleConfirmation(assessmentId, courseCode, assessmentName) {
    const overlay = document.getElementById('unschedule-overlay');
    const dialog = document.getElementById('unschedule-confirm');
    const nameSpan = document.getElementById('assessment-name-confirm');
    const idInput = document.getElementById('unschedule-assessment-id');
    
    // Set confirmation text and store the assessment ID
    nameSpan.textContent = `${courseCode}-${assessmentName}`;
    idInput.value = assessmentId;
    
    // Show the overlay and dialog
    overlay.style.display = 'block';
    dialog.style.display = 'block';
    
    // Add event listeners to buttons
    const confirmBtn = document.getElementById('confirm-unschedule-btn');
    const cancelBtn = document.getElementById('cancel-unschedule-btn');
    
    // Remove any existing listeners
    const newConfirmBtn = confirmBtn.cloneNode(true);
    const newCancelBtn = cancelBtn.cloneNode(true);
    
    confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
    cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
    
    // Add new listeners
    newConfirmBtn.addEventListener('click', function() {
      // Close the dialog
      closeUnscheduleConfirmation();
      
      // Unschedule the assessment
      unscheduleEvent(idInput.value);
    });
    
    newCancelBtn.addEventListener('click', closeUnscheduleConfirmation);
    
    // Close when clicking on the overlay
    overlay.addEventListener('click', closeUnscheduleConfirmation);
    
    // Close on Escape key
    document.addEventListener('keydown', function escapeHandler(e) {
      if (e.key === 'Escape') {
        closeUnscheduleConfirmation();
        document.removeEventListener('keydown', escapeHandler);
      }
    });
  }

  // Function to close the unschedule confirmation dialog
  function closeUnscheduleConfirmation() {
    const overlay = document.getElementById('unschedule-overlay');
    const dialog = document.getElementById('unschedule-confirm');
    
    overlay.style.display = 'none';
    dialog.style.display = 'none';
  }

  // Add this function to check if dark mode is active
  function isDarkModeActive() {
    return document.body.classList.contains('dark-mode') || 
           document.documentElement.classList.contains('dark-mode') || 
           localStorage.getItem('darkMode') === 'true';
  }

  // Update showUnscheduleConfirm function to add dark mode class if needed
  function showUnscheduleConfirm(assessmentId, assessmentName) {
    const confirmDialog = document.getElementById('unschedule-confirm');
    const overlay = document.getElementById('unschedule-overlay');
    const nameSpan = document.getElementById('assessment-name-confirm');
    const idInput = document.getElementById('unschedule-assessment-id');
    
    if (confirmDialog && overlay && nameSpan && idInput) {
      nameSpan.textContent = assessmentName;
      idInput.value = assessmentId;
      
      // Apply dark mode if active
      if (isDarkModeActive()) {
        confirmDialog.classList.add('dark-mode');
        overlay.classList.add('dark-mode');
      } else {
        confirmDialog.classList.remove('dark-mode');
        overlay.classList.remove('dark-mode');
      }
      
      confirmDialog.style.display = 'block';
      overlay.style.display = 'block';
      
      // Add event listeners to buttons
      const confirmBtn = document.getElementById('confirm-unschedule-btn');
      const cancelBtn = document.getElementById('cancel-unschedule-btn');
      
      if (confirmBtn) {
        confirmBtn.onclick = function() {
          unscheduleEvent(assessmentId);
          confirmDialog.style.display = 'none';
          overlay.style.display = 'none';
        };
      }
      
      if (cancelBtn) {
        cancelBtn.onclick = function() {
          confirmDialog.style.display = 'none';
          overlay.style.display = 'none';
        };
      }
      
      // Close on overlay click
      overlay.onclick = function() {
        confirmDialog.style.display = 'none';
        overlay.style.display = 'none';
      };
    }
  }

  // Add theme change listener to update modals if they're visible
  document.addEventListener('themeToggled', function() {
    const isDark = isDarkModeActive();
    
    // Update the clash modal if visible
    const clashModal = document.getElementById('clash-modal');
    const clashOverlay = document.getElementById('clash-modal-overlay');
    
    if (clashModal && !clashModal.classList.contains('hidden')) {
      if (isDark) {
        clashModal.classList.add('dark-mode');
        clashOverlay.classList.add('dark-mode');
      } else {
        clashModal.classList.remove('dark-mode');
        clashOverlay.classList.remove('dark-mode');
      }
    }
    
    // Update unschedule confirm if visible
    const unscheduleConfirm = document.getElementById('unschedule-confirm');
    const unscheduleOverlay = document.getElementById('unschedule-overlay');
    
    if (unscheduleConfirm && unscheduleConfirm.style.display !== 'none') {
      if (isDark) {
        unscheduleConfirm.classList.add('dark-mode');
        unscheduleOverlay.classList.add('dark-mode');
      } else {
        unscheduleConfirm.classList.remove('dark-mode');
        unscheduleOverlay.classList.remove('dark-mode');
      }
    }
    
    // Update any active loading indicator
    const loadingIndicator = document.querySelector('.loading-indicator');
    if (loadingIndicator) {
      if (isDark) {
        loadingIndicator.classList.add('dark-mode');
      } else {
        loadingIndicator.classList.remove('dark-mode');
      }
    }
  });

  // Initialize external events
  document.addEventListener('DOMContentLoaded', function() {
    // Style setup for feedback indicators
    const style = document.createElement('style');
    style.textContent = `
      .schedule-feedback {
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        padding: 10px 20px;
        color: white;
        border-radius: 4px;
        z-index: 9999;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        animation: fadeInOut 3s ease forwards;
        display: flex;
        align-items: center;
        gap: 8px;
      }
      
      .schedule-feedback.success {
        background-color: #4cd964;
      }
      
      .schedule-feedback.cancel {
        background-color: #ff9500;
      }
      
      .schedule-feedback.error {
        background-color: #ff3b30;
      }
      
      @keyframes fadeInOut {
        0% { opacity: 0; }
        10% { opacity: 1; }
        80% { opacity: 1; }
        100% { opacity: 0; }
      }
      
      .loading-indicator {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background-color: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 15px;
      }
      
      .loading-indicator.dark-mode {
        background-color: rgba(33, 33, 33, 0.9);
        color: #fff;
      }
      
      .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #5e72e4;
        border-radius: 50%;
        animation: spin 1s linear infinite;
      }
      
      .dark-mode .spinner {
        border: 4px solid #333;
        border-top: 4px solid #5e72e4;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      .loading-text {
        font-size: 14px;
        font-weight: 500;
      }
      
      .badge.recovered {
        background-color: #f5a623;
        color: white;
        animation: pulse 2s infinite;
      }
      
      @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
      }
      
      .draggable-assessment.recovered {
        animation: highlightCard 2s ease-in-out;
        box-shadow: 0 0 10px rgba(245, 166, 35, 0.7);
      }
      
      @keyframes highlightCard {
        0% { background-color: rgba(245, 166, 35, 0.3); }
        100% { background-color: transparent; }
      }
      
      /* Enhanced recovery visual */
      .draggable-assessment.recovered::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border: 2px solid #f5a623;
        border-radius: inherit;
        animation: pulseBorder 1.5s ease-out;
        pointer-events: none;
      }
      
      @keyframes pulseBorder {
        0% { 
          box-shadow: 0 0 0 0 rgba(245, 166, 35, 0.7);
          opacity: 1;
        }
        70% { 
          box-shadow: 0 0 0 10px rgba(245, 166, 35, 0);
          opacity: 0.7;
        }
        100% { 
          box-shadow: 0 0 0 0 rgba(245, 166, 35, 0);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
    
    // Rest of initialization code
    // ... existing code ...
  });

  // Function to refresh the assessment list
  function refreshCurrentAssessments() {
    console.log("Refreshing current assessments");
    
    // Show loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.className = 'loading-indicator' + (isDarkModeActive() ? ' dark-mode' : '');
    loadingIndicator.innerHTML = '<div class="spinner"></div><div class="loading-text">Refreshing...</div>';
    document.body.appendChild(loadingIndicator);
    
    // Fetch updated assessments for the current user and semester
    fetch('/api/my_semester_assessments')
      .then(response => {
        if (!response.ok) {
          throw new Error(`Server returned ${response.status}: ${response.statusText}`);
        }
        return response.json();
      })
      .then(data => {
        if (data.success) {
          // Refresh the calendar
          calendar.refetchEvents();
          
          // Update the unscheduled assessment list
          updateAssessmentList(data.assessments);
          console.log("Successfully refreshed assessments", data.assessments);
        } else {
          console.error("Failed to refresh assessments:", data.message);
          // Fallback to rebuilding the list from current DOM state
          rebuildAssessmentListFromCurrentState();
        }
      })
      .catch(error => {
        console.error("Error refreshing assessments:", error);
        // Fallback to rebuilding the list from current DOM state
        rebuildAssessmentListFromCurrentState();
      })
      .finally(() => {
        // Always apply filters after refresh
        setTimeout(applyFilters, 200);
        
        // Remove loading indicator
        if (loadingIndicator.parentNode) {
          loadingIndicator.parentNode.removeChild(loadingIndicator);
        }
      });
  }
  
  // Function to rebuild assessment list from current DOM state when API fails
  function rebuildAssessmentListFromCurrentState() {
    console.log("Using fallback to rebuild assessment list");
    const unscheduledList = document.getElementById('unscheduled-list');
    
    // If we have any scheduled items in the calendar that aren't in the unscheduled list,
    // make sure they're added back to the list
    const calendarEvents = calendar.getEvents();
    const existingItems = Array.from(unscheduledList.querySelectorAll('.draggable-assessment'))
      .map(el => el.dataset.assessmentId);
    
    // Force the calendar to render all events
    calendar.render();
    
    // Make all existing assessment elements draggable again
    new FullCalendar.Draggable(unscheduledList, {
      itemSelector: ".draggable-assessment.can-drag",
      eventData: function(eventEl) {
        return {
          id: eventEl.dataset.assessmentId,
          title: `${eventEl.dataset.courseCode}-${eventEl.dataset.name || eventEl.children[0].innerText.split('-')[1]} (${eventEl.dataset.percentage}%)`,
          backgroundColor: eventEl.dataset.proctored === "1" || eventEl.dataset.proctored === "True" || eventEl.dataset.proctored === "true" ? colors.Proctored : colors.Assignment,
          textColor: '#fff',
          extendedProps: {
            course_code: eventEl.dataset.courseCode,
            percentage: eventEl.dataset.percentage,
            proctored: eventEl.dataset.proctored === "1" || eventEl.dataset.proctored === "True" || eventEl.dataset.proctored === "true",
            isRescheduling: eventEl.classList.contains('scheduled'),
            assessmentName: eventEl.dataset.name
          }
        };
      },
      mirrorSelector: ".draggable-assessment",
      dragRevertDuration: 0,
      droppableScope: 'assessment',
      dragClass: 'is-dragging',
      mirrorClass: 'assessment-mirror'
    });
    
    // Make all items visible by default, filtering will be applied later
    Array.from(unscheduledList.querySelectorAll('.draggable-assessment')).forEach(el => {
      el.style.display = 'block';
    });
  }
  
  // Function to update the assessment list with new data
  function updateAssessmentList(assessments) {
    const unscheduledList = document.getElementById('unscheduled-list');
    if (!unscheduledList) return;
    
    // Get everything except the h3, instructions and info elements
    const listHeader = unscheduledList.querySelector('h3');
    const dragInstructions = unscheduledList.querySelector('.drag-instructions');
    const dateRangeInfo = unscheduledList.querySelector('.date-range-info');
    
    // Clear existing assessments
    unscheduledList.innerHTML = '';
    
    // Add back the header
    if (listHeader) unscheduledList.appendChild(listHeader);
    
    // Add assessments
    if (assessments && assessments.length > 0) {
      for (const assessment of assessments) {
        const isScheduled = assessment.scheduled !== null;
        
        const assessmentEl = document.createElement('div');
        assessmentEl.className = `draggable-assessment ${assessment.proctored ? 'proctored' : ''} ${isScheduled ? 'scheduled' : 'status-unscheduled'} can-drag`;
        assessmentEl.dataset.assessmentId = assessment.id;
        assessmentEl.dataset.courseCode = assessment.course_code;
        assessmentEl.dataset.percentage = assessment.percentage;
        assessmentEl.dataset.proctored = assessment.proctored;
        assessmentEl.dataset.scheduled = isScheduled ? assessment.scheduled : 'false';
        assessmentEl.dataset.name = assessment.name;
        
        assessmentEl.innerHTML = `
          <span class="assessment-name">${assessment.course_code}-${assessment.name}</span>
          <div class="assessment-details">
            Weight: ${assessment.percentage}%
            <div class="badge-container">
              ${isScheduled ? '<span class="status-badge scheduled">Scheduled</span>' : '<span class="status-badge unscheduled">Unscheduled</span>'}
              ${assessment.proctored ? '<span class="badge proctored">Proctored</span>' : ''}
            </div>
            ${isScheduled ? `<div>Date: ${assessment.scheduled}</div>` : ''}
          </div>
        `;
        
        unscheduledList.appendChild(assessmentEl);
      }
    } else {
      const noAssessmentsMsg = document.createElement('p');
      noAssessmentsMsg.textContent = 'No assessments found for your courses in the active semester.';
      unscheduledList.appendChild(noAssessmentsMsg);
    }
    
    // Add back the instructions and info
    if (dragInstructions) unscheduledList.appendChild(dragInstructions);
    if (dateRangeInfo) unscheduledList.appendChild(dateRangeInfo);
    
    // Reinitialize draggable functionality
    new FullCalendar.Draggable(unscheduledList, {
      itemSelector: ".draggable-assessment.can-drag",
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
            isRescheduling: eventEl.classList.contains('scheduled'),
            assessmentName: eventEl.dataset.name
          }
        };
      }
    });
    
    // Apply current filters
    setTimeout(applyFilters, 100);
  }
}); 