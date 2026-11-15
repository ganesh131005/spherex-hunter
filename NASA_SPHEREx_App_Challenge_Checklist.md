# NASA SPHEREx App Challenge – Final Judge Evaluation Checklist

**Purpose:** Use this checklist to inspect whether the application meets the challenge requirements and is scientifically reliable.

**How to use it:** Mark each item as:
- `[ ]` Not checked
- `[x]` Passed
- `[!]` Needs improvement
- `[N/A]` Not applicable

A failed item is a warning to investigate, not automatically an official NASA rejection rule. This is a practical evaluation checklist, not an official NASA scoring rubric.

---

## 1. Application Basics and User Interface (1–8)

1. [ ] **The application opens successfully.**  
   What I should see: The website loads without crashing or showing a blank page.  
   Reason for rejection concern: The application cannot be accessed or used.

2. [ ] **The purpose of the application is explained clearly.**  
   What I should see: A short explanation that the tool explores SPHEREx observations over time.  
   Reason for rejection concern: Users cannot understand what the application is designed to do.

3. [ ] **The interface is easy to understand.**  
   What I should see: Clearly named buttons, fields, tabs and controls.  
   Reason for rejection concern: Users cannot work out how to use the main features.

4. [ ] **The application gives instructions for first-time users.**  
   What I should see: Simple guidance explaining how to enter coordinates and view observations.  
   Reason for rejection concern: Users are left guessing how to begin.

5. [ ] **The application works on common screen sizes.**  
   What I should see: The main controls and images remain usable on desktop and smaller screens.  
   Reason for rejection concern: Important features are hidden or unusable on typical devices.

6. [ ] **Loading and processing states are visible.**  
   What I should see: A message or indicator while data is being retrieved or processed.  
   Reason for rejection concern: The application appears frozen or gives no feedback.

7. [ ] **Errors are explained in understandable language.**  
   What I should see: Helpful messages when coordinates are invalid, data is unavailable or a request fails.  
   Reason for rejection concern: The application fails silently or displays confusing technical errors.

8. [ ] **The application identifies the data source.**  
   What I should see: Clear attribution to SPHEREx/NASA data and links or references to relevant documentation.  
   Reason for rejection concern: Users cannot tell where the scientific data came from.

---

## 2. RA/Dec Coordinate Search (9–16)

9. [ ] **The user can enter Right Ascension (RA).**  
   What I should see: An input field for RA with its accepted format explained.  
   Reason for rejection concern: The user cannot specify the sky location.

10. [ ] **The user can enter Declination (Dec).**  
    What I should see: An input field for Dec with its accepted format explained.  
    Reason for rejection concern: The coordinate search is incomplete.

11. [ ] **The accepted coordinate formats are clear.**  
    What I should see: The application explains whether it accepts decimal degrees, hours/minutes/seconds or another supported format.  
    Reason for rejection concern: Users enter valid coordinates in a format the application does not explain or support.

12. [ ] **Coordinate values are validated.**  
    What I should see: Invalid or out-of-range values are rejected with a helpful message.  
    Reason for rejection concern: Incorrect coordinates are silently accepted and may retrieve the wrong region.

13. [ ] **The application searches the correct sky location.**  
    What I should see: The displayed region corresponds to the submitted RA and Dec.  
    Reason for rejection concern: The application displays data from a different location.

14. [ ] **The user can choose the size of the sky region, if supported.**  
    What I should see: A clearly labelled field-of-view or search-area control.  
    Reason for rejection concern: The displayed area is unclear or cannot be controlled when the feature is claimed.

15. [ ] **The search can be repeated for another location.**  
    What I should see: Users can change the coordinates and run a new search without restarting the application.  
    Reason for rejection concern: The tool only works for one fixed example.

16. [ ] **The searched coordinates are shown with the results.**  
    What I should see: The selected RA and Dec remain visible so users know which region they are exploring.  
    Reason for rejection concern: Users cannot verify which location the displayed observations represent.

---

## 3. SPHEREx Data Retrieval (17–24)

17. [ ] **The application retrieves genuine SPHEREx data.**  
    What I should see: Data obtained from an authentic SPHEREx archive, service or documented data source.  
    Reason for rejection concern: The application uses invented, unrelated or merely decorative data while presenting it as SPHEREx data.

18. [ ] **The data source and access method are documented.**  
    What I should see: The archive/API or data product used is identified.  
    Reason for rejection concern: The origin of the data cannot be verified.

19. [ ] **The application retrieves observations for the requested region.**  
    What I should see: Returned records match the submitted sky coordinates and search area.  
    Reason for rejection concern: Search results are unrelated to the requested location.

20. [ ] **Observation dates or times are retrieved.**  
    What I should see: Each observation has its associated date/time or epoch information.  
    Reason for rejection concern: Observations cannot be placed in chronological order.

21. [ ] **Multiple observations are supported when available.**  
    What I should see: The application can retrieve more than one observation of the same region when the archive contains them.  
    Reason for rejection concern: The central time-comparison purpose is not demonstrated.

22. [ ] **Missing observations are handled properly.**  
    What I should see: A clear message when no data exists for a location or time.  
    Reason for rejection concern: The application invents observations or crashes when data is missing.

23. [ ] **The application distinguishes real data from demonstration data.**  
    What I should see: Any mock, sample or simulated data is explicitly labelled.  
    Reason for rejection concern: Demonstration data is misrepresented as real telescope data.

24. [ ] **Data retrieval failures are handled safely.**  
    What I should see: A useful error message and a way to retry or change the search.  
    Reason for rejection concern: Temporary archive or network failures make the application unusable.

---

## 4. Astronomical Image Viewer (25–32)

25. [ ] **Retrieved observations are displayed as images or usable visual data.**  
    What I should see: The user can inspect the selected sky region.  
    Reason for rejection concern: The application retrieves data but does not make it viewable.

26. [ ] **The image is associated with the correct observation.**  
    What I should see: The image and its date, band and other relevant metadata are connected correctly.  
    Reason for rejection concern: Images are labelled with incorrect observation information.

27. [ ] **Image scale and orientation are handled consistently.**  
    What I should see: The sky region is presented with a clear scale and orientation.  
    Reason for rejection concern: Users may mistake display changes for astronomical movement.

28. [ ] **The user can zoom in and out, if supported.**  
    What I should see: Zoom controls or another clear way to inspect details.  
    Reason for rejection concern: Important objects cannot be inspected at a useful scale.

29. [ ] **The user can move around the image, if supported.**  
    What I should see: Panning or navigation controls for exploring the region.  
    Reason for rejection concern: The user cannot inspect the full selected area.

30. [ ] **Image brightness or contrast can be adjusted, if supported.**  
    What I should see: Display controls that make faint and bright features easier to inspect.  
    Reason for rejection concern: Features are hidden by an unsuitable display stretch or scaling.

31. [ ] **The image display explains its units or scaling.**  
    What I should see: The application identifies whether values are counts, calibrated flux, surface brightness or display-scaled values.  
    Reason for rejection concern: Users interpret detector counts or display values as physical brightness without justification.

32. [ ] **Image quality or data-quality information is available.**  
    What I should see: Relevant quality indicators, flags or limitations are shown when available.  
    Reason for rejection concern: Poor-quality data is presented as fully reliable without warning.

---

## 5. Time-Based Comparison and Animation (33–40)

33. [ ] **The application displays more than one epoch when available.**  
    What I should see: The user can select different observations of the same region.  
    Reason for rejection concern: The time-based comparison requirement is not demonstrated.

34. [ ] **Observations are arranged in chronological order.**  
    What I should see: Earlier observations appear before later observations.  
    Reason for rejection concern: The sequence gives a misleading picture of changes over time.

35. [ ] **The user can move to the next observation.**  
    What I should see: A next control or equivalent navigation.  
    Reason for rejection concern: Users cannot compare observations individually.

36. [ ] **The user can move to the previous observation.**  
    What I should see: A previous control or equivalent navigation.  
    Reason for rejection concern: Users cannot review the sequence in both directions.

37. [ ] **The observations can be played as an animation or video-like sequence.**  
    What I should see: A play control that steps through available observations.  
    Reason for rejection concern: The central visual time-series feature is missing.

38. [ ] **The user can pause and resume playback.**  
    What I should see: Playback controls that work reliably.  
    Reason for rejection concern: Users cannot inspect a feature at a particular observation.

39. [ ] **The playback speed can be controlled, if supported.**  
    What I should see: A speed setting or frame interval control.  
    Reason for rejection concern: The animation is too fast or too slow to inspect, if speed control is claimed.

40. [ ] **The date/time of the current frame is visible.**  
    What I should see: The selected observation's date or epoch changes with each frame.  
    Reason for rejection concern: Users cannot tell when each image was taken.

---

## 6. Movement Detection and Analysis (41–47)

41. [ ] **The application helps users compare object positions across observations.**  
    What I should see: The same sky region can be inspected at different times.  
    Reason for rejection concern: The application shows a sequence but provides no practical way to inspect positional changes.

42. [ ] **Images are aligned before positional changes are interpreted.**  
    What I should see: A consistent sky reference or documented alignment method.  
    Reason for rejection concern: Small pointing differences are mistaken for object movement.

43. [ ] **The application can highlight possible moving objects, if this feature is claimed.**  
    What I should see: Candidate locations or changes are marked clearly.  
    Reason for rejection concern: The application claims automatic detection but does not produce verifiable results.

44. [ ] **Possible detections can be checked against the original images.**  
    What I should see: Users can inspect the source observations behind a detection.  
    Reason for rejection concern: A detection cannot be independently checked.

45. [ ] **Real movement is distinguished from image artifacts.**  
    What I should see: The method considers alignment, noise, detector effects and data-quality flags.  
    Reason for rejection concern: Noise, bad pixels or processing artifacts are reported as moving astronomical objects.

46. [ ] **Movement measurements include units and time information.**  
    What I should see: Any reported positional change or motion rate has clear units and uses the observation dates.  
    Reason for rejection concern: Movement values are unexplained or calculated using incorrect time intervals.

47. [ ] **Uncertain detections are labelled as candidates, not confirmed discoveries.**  
    What I should see: Appropriate wording such as “possible candidate” where evidence is incomplete.  
    Reason for rejection concern: The application overstates what its data can prove.

---

## 7. Brightness and Image Comparison (48–54)

48. [ ] **The application allows brightness comparison across observations.**  
    What I should see: A way to inspect how the measured signal changes over time.  
    Reason for rejection concern: Brightness changes, one of the challenge's scientific goals, cannot be explored.

49. [ ] **Brightness measurements use a consistent method.**  
    What I should see: Measurements account for relevant calibration, background and image-processing differences.  
    Reason for rejection concern: Changes in display settings or detector response are mistaken for real brightness changes.

50. [ ] **A brightness-versus-time graph is available, if supported.**  
    What I should see: A light curve with observation time on one axis and measured brightness or flux on the other.  
    Reason for rejection concern: A claimed light-curve feature is missing or its axes are not explained.

51. [ ] **Image subtraction is scientifically appropriate, if used.**  
    What I should see: Images are aligned and made comparable before one is subtracted from another.  
    Reason for rejection concern: Misaligned or differently scaled images create misleading difference signals.

52. [ ] **Difference images are labelled clearly.**  
    What I should see: The application explains which observations were compared and what positive or negative differences mean.  
    Reason for rejection concern: Users cannot interpret the difference image.

53. [ ] **Measurement units are displayed.**  
    What I should see: Units such as counts, flux density or surface brightness are identified accurately.  
    Reason for rejection concern: Detector counts are incorrectly described as calibrated physical brightness.

54. [ ] **Uncertainty or data-quality limitations are shown where available.**  
    What I should see: Error estimates, quality flags or warnings accompany measurements when provided by the data.  
    Reason for rejection concern: Measurements appear more certain than the data supports.

---

## 8. Spectral Analysis and the 102 Bands (55–60)

55. [ ] **The application explains the 102 spectral bands accurately.**  
    What I should see: A simple explanation that SPHEREx measures infrared light in many wavelength ranges.  
    Reason for rejection concern: The application gives an incorrect description of the instrument or its bands.

56. [ ] **The user can inspect wavelength information, if supported.**  
    What I should see: A wavelength or band selector with clear labels and units.  
    Reason for rejection concern: A claimed spectral exploration feature cannot be used or verified.

57. [ ] **The application identifies the wavelength or band for displayed data.**  
    What I should see: The selected band or wavelength is shown beside the image or measurement.  
    Reason for rejection concern: Users cannot tell which part of the infrared spectrum they are viewing.

58. [ ] **A spectrum is plotted with correctly labelled axes, if supported.**  
    What I should see: Wavelength on the horizontal axis and an appropriate measured quantity on the vertical axis.  
    Reason for rejection concern: The graph is mislabelled or does not represent spectral measurements.

59. [ ] **Spectral measurements are not confused with time measurements.**  
    What I should see: The application clearly distinguishes changes across wavelength from changes across observation date.  
    Reason for rejection concern: The user is shown a graph but cannot tell whether it represents time or wavelength.

60. [ ] **Molecular or object interpretations are cautious and evidence-based.**  
    What I should see: Any discussion of water, methane, carbon dioxide or other signatures is supported by suitable data and limitations.  
    Reason for rejection concern: The application claims to identify molecules or object types without adequate scientific evidence.

---

## 9. Scientific Validation and Required Test Targets (61–67)

61. [ ] **Barnard’s Star can be used as a test target.**  
    What I should see: The application can search for and inspect this target using suitable coordinates or a target lookup.  
    Reason for rejection concern: A required example target cannot be tested without explanation.

62. [ ] **Epsilon Indi B can be used as a test target.**  
    What I should see: The application can locate or attempt to retrieve relevant observations and clearly report data availability.  
    Reason for rejection concern: The target is not tested or missing data is hidden.

63. [ ] **WISE 0855 can be used as a test target.**  
    What I should see: The application can search for the target using its supplied coordinates or a verified target lookup.  
    Reason for rejection concern: The application cannot demonstrate the workflow on this named target.

64. [ ] **RW Aurigae can be used as a test target.**  
    What I should see: The application can locate or attempt to retrieve relevant observations and show their availability.  
    Reason for rejection concern: The target is omitted or results are not verifiable.

65. [ ] **R Draconis can be used as a test target.**  
    What I should see: The application can locate or attempt to retrieve relevant observations and show their availability.  
    Reason for rejection concern: The target is omitted or results are not verifiable.

66. [ ] **Target coordinates and names are checked against a reliable source.**  
    What I should see: Target names resolve to the intended astronomical objects, with coordinates and identifiers checked.  
    Reason for rejection concern: A name is matched to the wrong object or inaccurate coordinates.

67. [ ] **The application reports when a target has insufficient or unavailable data.**  
    What I should see: A clear explanation rather than fabricated images, dates or measurements.  
    Reason for rejection concern: The application invents results to make every test appear successful.

---

## 10. Performance, Reliability and Presentation (68–70)

68. [ ] **The application performs reliably with realistic data volumes.**  
    What I should see: Retrieval, display and comparison work without frequent crashes or severe delays.  
    Reason for rejection concern: The application cannot handle its intended workflow.

69. [ ] **The code and workflow can be explained and reproduced.**  
    What I should see: The team can explain where data comes from, how it is processed and how results are produced.  
    Reason for rejection concern: The team cannot explain or reproduce its own scientific outputs.

70. [ ] **The final demonstration shows the complete user journey.**  
    What I should see: Enter coordinates, retrieve observations, inspect dates, play or step through the sequence, and examine movement or brightness changes.  
    Reason for rejection concern: The demonstration shows isolated screens but does not prove that the main workflow works.

---

## Highest-Priority Warning Signs

Investigate these issues immediately because they can seriously weaken the project:

- The application presents sample or invented data as genuine SPHEREx observations.
- The user cannot search by RA and Dec.
- Only one observation is shown when multiple observations are available.
- Observations are not associated with the correct dates or sky location.
- Images are not aligned before movement is interpreted.
- Noise, bad pixels or image artifacts are reported as real moving objects.
- Detector counts are presented as calibrated physical brightness without the required conversion.
- Brightness comparisons ignore calibration or incompatible image scaling.
- The application claims a discovery or molecular identification that the data does not support.
- Missing data is hidden or replaced with fabricated results.
- The team cannot explain the data source, processing steps or scientific limitations.

## Final Review Before Submission

- [ ] The main workflow works from coordinate entry to time-based comparison.
- [ ] The application uses genuine SPHEREx data, or clearly labels any demonstration data.
- [ ] Every displayed observation has traceable date/time and source information.
- [ ] Images are aligned appropriately before scientific comparisons.
- [ ] Movement and brightness results are supported by measurements.
- [ ] Units, uncertainty and data-quality limitations are explained.
- [ ] All five named test targets have been tested, with unavailable data reported honestly.
- [ ] The team can explain and demonstrate the complete application.

---

**Reminder:** This is a practical 70-point development and judging checklist assembled to help evaluate the app. It is not an official NASA rejection list or official NASA scoring system. Optional features such as spectral graphs, automatic object detection or overlays should be judged according to what the team claims to implement; their absence alone does not mean automatic rejection.
