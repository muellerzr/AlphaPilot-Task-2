# Post processing algorithm
#
# This program proprietary to Team Titans of AlphaPilot Challenge
# Authors: Carson Wilber
# Team Captain: Ashok Yannam
#---------------------------------------------------#

ordered_corner_keys = ["UL", "UR", "LR", "LL"]

def ordered_xy_predictions_to_dict(ordered_xy_predictions):
  corner_dict = dict()

  for x, y, k, i in zip(ordered_xy_predictions[::2], ordered_xy_predictions[1::2], ordered_corner_keys, range(4)):
    if not (x == 0 and y == 0):
      corner_dict[k] = ordered_xy_predictions[2*i:2*(i+1)]

  return corner_dict

def sub(arr_a, arr_b):
  arr_c = []
  for elem_a, elem_b in zip(arr_a, arr_b):
    arr_c += [elem_a - elem_b]
  return arr_c

def add(arr_a, arr_b):
  arr_c = []
  for elem_a, elem_b in zip(arr_a, arr_b):
    arr_c += [elem_a + elem_b]
  return arr_c

''' Case I. 3 Corners. Knowns: all x and y except missing corner, width, height, and rotation. '''
def case_i(existing_corners):
  corners = existing_corners

  if "UL" not in existing_corners:
    corners["UL"] = sub(add(existing_corners["UR"], existing_corners["LL"]), existing_corners["LR"])
  elif "UR" not in existing_corners:
    corners["UR"] = sub(add(existing_corners["LR"], existing_corners["UL"]), existing_corners["LL"])
  elif "LR" not in existing_corners:
    corners["LR"] = sub(add(existing_corners["LL"], existing_corners["UR"]), existing_corners["UL"])
  else: # "LL" not in existing_corners
    corners["LL"] = sub(add(existing_corners["UL"], existing_corners["LR"]), existing_corners["UR"])

  return corners

''' Case IIa. Corners are opposing. Knowns: x_left, x_right, y_top, y_bottom, width, height, and rotation. '''
def case_ii_a(existing_corners):
  corners = existing_corners

  if "UL" not in existing_corners: # "LR" also not in existing_corners
    corners["UL"] = [existing_corners["LL"][0], existing_corners["UR"][1]]
  else: # "UR" and "LL" not in existing_corners
    corners["UR"] = [existing_corners["LR"][0], existing_corners["UL"][1]]

  return case_i(corners)

''' Case IIb. Corners are same side. Knowns: one x and two y OR two x and one y, width, height. '''
def case_ii_b(existing_corners):
  corners = existing_corners
  
  existing_values = [list(v) for v in corners.values()]
  width = abs(existing_values[0][0] - existing_values[1][0])
  height = abs(existing_values[0][1] - existing_values[1][1])

  # Case IIb-1. Side is left or right. Knowns: y_upper, y_lower, midpoint x, height.
  if "UL" in existing_corners and "LL" in existing_corners:
    corners["UR"] = [existing_corners["UL"][0] + height, existing_corners["UL"][1]] # * rotation?
    corners["LR"] = [existing_corners["LL"][0] + height, existing_corners["LL"][1]] # * rotation?
  elif "UR" in existing_corners and "LR" in existing_corners:
    corners["UL"] = [existing_corners["UR"][0] - height, existing_corners["UR"][1]] # * rotation?
    corners["LL"] = [existing_corners["LR"][0] - height, existing_corners["LR"][1]] # * rotation?

  # Case IIb-2. Side is top or bottom. Knowns: x_left, x_right, midpoint y, width.
  elif "UL" in existing_corners and "UR" in existing_corners:
    corners["LL"] = [existing_corners["UL"][0], existing_corners["UL"][1] + width] # * rotation?
    corners["LR"] = [existing_corners["UR"][0], existing_corners["UR"][1] + width] # * rotation?
  else: # "LL" in existing_corners and "LR" in existing_corners
    corners["UL"] = [existing_corners["LL"][0], existing_corners["LL"][1] - width] # * rotation?
    corners["UR"] = [existing_corners["LR"][0], existing_corners["LR"][1] - width] # * rotation?

  return corners

''' Case II. 2 Corners. '''
def case_ii(existing_corners):
  if "UL" in existing_corners and "LR" in existing_corners:
    return case_ii_a(existing_corners)
  elif "UR" in existing_corners and "LL" in existing_corners:
    return case_ii_a(existing_corners)
  else: # Sides are (UL, UR), (LL, LR), (UL, LL), or (UR, LR)
    return case_ii_b(existing_corners)

def calculate_missing_corners(predictions):
  existing_corners = ordered_xy_predictions_to_dict(predictions)
  results = []
  
  if len(existing_corners) == 3:
    results = case_i(existing_corners)
  elif len(existing_corners) == 2:
    results = case_ii(existing_corners)
  elif len(existing_corners) == 1:
    print("Cannot calculate missing corners for Case III (1 Corner.)")
    results = existing_corners
  else:
    if len(existing_corners) == 0:
      print("Cannot calculate missing corners with no known corners at all!")
    results = existing_corners
  
  xy = []
  for corner in [results[clazz] if clazz in results else [0, 0] for clazz in ordered_corner_keys]:
    xy.extend(corner)
  return xy

def bad_xy_to_good_xy(model_output):
    model_corrected = model_output
    
    xs = model_output[:8:2]
    ys = model_output[1:8:2]
    
    num_missing = sum([1 if x == 0 and y == 0 else 0 for x, y in zip(xs, ys)])

    # If all corners classified, check classifications are accurate
    if num_missing == 0:
        midpoint_x = sum(xs)/4.
        midpoint_y = sum(ys)/4.
        
        corners_fixed = dict()
        
        for x, y in zip(xs, ys):
            if x <= midpoint_x and y <= midpoint_y and not "UL" in corners_fixed:
                corners_fixed["UL"] = [x, y]
            elif x > midpoint_x and y <= midpoint_y and not "UR" in corners_fixed:
                corners_fixed["UR"] = [x, y]
            elif x > midpoint_x and y > midpoint_y and not "LR" in corners_fixed:
                corners_fixed["LR"] = [x, y]
            elif x <= midpoint_x and y > midpoint_y and not "LL" in corners_fixed:
                corners_fixed["LL"] = [x, y]

        num_missing = 4 - len(corners_fixed)
        model_corrected = []
        for corner_key in ordered_corner_keys:
            if corner_key in corners_fixed:
                model_corrected.extend(corners_fixed[corner_key])
            else:
                model_corrected.extend([0, 0])

    # If any corners are missing, call missing_corners algorithm
    if num_missing > 0:
        if num_missing <= 2:
            model_corrected = calculate_missing_corners(model_output)
        else:
            model_corrected = []
    
    return model_corrected
