import random
from typing import Dict, List, Any, Optional
from models import UIElement, Observation, Action, Reward, TaskInfo, EnvironmentState, ActionType

# Penalty constants for robust reward system
PENALTY_HALLUCINATION = -0.1
PENALTY_INVALID_VALUE = -0.05

class OmniAuditEnvironment:
    """OmniAudit Environment - Hybrid E-commerce audit simulation"""
    
    def __init__(self):
        self.backend_database = {}
        self.frontend_ui_tree = {}
        self.material_specs = {}
        self.state = EnvironmentState()
        self.tasks = self._initialize_tasks()
        self.current_scenario = None
        self._reset_environment()
    
    def _initialize_tasks(self) -> Dict[str, TaskInfo]:
        """Initialize all available tasks"""
        return {
            "easy": TaskInfo(
                name="Fix Missing Aria Label",
                description="Add missing aria-label to a Buy button for accessibility compliance",
                difficulty="easy",
                reward_weight=0.3
            ),
            "medium": TaskInfo(
                name="Fix Price Mismatch", 
                description="Resolve price discrepancy between UI display and backend database",
                difficulty="medium",
                reward_weight=0.7
            ),
            "hard": TaskInfo(
                name="Resolve Semantic Conflict",
                description="Fix material specification conflict between backend and UI using secondary specs",
                difficulty="hard",
                reward_weight=1.0
            )
        }
    
    def _get_product_scenarios(self) -> List[Dict[str, Any]]:
        """Define multiple product scenarios for dynamic generalization"""
        return [
            {
                "name": "Silk Dress",
                "product_id": "PROD_001",
                "backend": {
                    "price": 29.99,
                    "sku": "SKU_12345",
                    "material": "Silk",
                    "category": "Clothing",
                    "stock": 15
                },
                "material_specs": {
                    "primary_material": "Silk",
                    "verified": True,
                    "supplier_notes": "Premium silk material, ethically sourced"
                },
                "ui_issues": {
                    "price_drift": 10.00,  # UI shows $10 less
                    "material_conflict": "Cotton"
                }
            },
            {
                "name": "Cotton Shirt",
                "product_id": "PROD_002",
                "backend": {
                    "price": 24.99,
                    "sku": "SKU_23456",
                    "material": "Cotton",
                    "category": "Clothing",
                    "stock": 32
                },
                "material_specs": {
                    "primary_material": "Cotton",
                    "verified": True,
                    "supplier_notes": "100% organic cotton, sustainably farmed"
                },
                "ui_issues": {
                    "price_drift": 12.50,  # UI shows $12.50 less
                    "material_conflict": "Polyester"
                }
            },
            {
                "name": "Wool Jacket",
                "product_id": "PROD_003",
                "backend": {
                    "price": 89.99,
                    "sku": "SKU_34567",
                    "material": "Wool",
                    "category": "Outerwear",
                    "stock": 8
                },
                "material_specs": {
                    "primary_material": "Wool",
                    "verified": True,
                    "supplier_notes": "Merino wool, temperature regulating"
                },
                "ui_issues": {
                    "price_drift": 15.00,  # UI shows $15 less
                    "material_conflict": "Fleece"
                }
            },
            {
                "name": "Linen Pants",
                "product_id": "PROD_004",
                "backend": {
                    "price": 45.99,
                    "sku": "SKU_45678",
                    "material": "Linen",
                    "category": "Clothing",
                    "stock": 21
                },
                "material_specs": {
                    "primary_material": "Linen",
                    "verified": True,
                    "supplier_notes": "Breathable linen fabric, summer collection"
                },
                "ui_issues": {
                    "price_drift": 11.25,  # UI shows $11.25 less
                    "material_conflict": "Rayon"
                }
            }
        ]
    
    def _reset_environment(self):
        """Reset environment with randomly selected product scenario"""
        # Randomly select a product scenario
        scenarios = self._get_product_scenarios()
        self.current_scenario = random.choice(scenarios)
        
        # Backend Database - Source of Truth
        self.backend_database = {
            "product_id": self.current_scenario["product_id"],
            **self.current_scenario["backend"]
        }
        
        # Material Specs - Secondary verification source
        self.material_specs = {
            self.current_scenario["product_id"]: self.current_scenario["material_specs"]
        }
        
        # Frontend UI Tree - Contains the issues to be fixed
        ui_price = self.backend_database["price"] - self.current_scenario["ui_issues"]["price_drift"]
        ui_material = self.current_scenario["ui_issues"]["material_conflict"]
        
        self.frontend_ui_tree = {
            "product_page": {
                "elements": [
                    {
                        "id": "buy-button",
                        "tag": "button",
                        "text": "Buy Now",
                        "attributes": {
                            "class": "btn btn-primary",
                            "onclick": f"addToCart('{self.current_scenario['product_id']}')"
                            # Missing aria-label for accessibility issue
                        }
                    },
                    {
                        "id": "price-display",
                        "tag": "span", 
                        "text": f"${ui_price:.2f}",  # Price mismatch - UI shows less than backend
                        "attributes": {
                            "class": "price",
                            "data-currency": "USD"
                        }
                    },
                    {
                        "id": "material-info",
                        "tag": "div",
                        "text": f"Material: {ui_material}",  # Semantic conflict - wrong material
                        "attributes": {
                            "class": "material-spec"
                        }
                    },
                    {
                        "id": "sku-display",
                        "tag": "span",
                        "text": f"SKU: {self.backend_database['sku']}",  # This one is correct
                        "attributes": {
                            "class": "sku"
                        }
                    }
                ]
            }
        }
        
        # Reset state
        self.state = EnvironmentState()
    
    def reset(self) -> Observation:
        """Reset the environment and return initial observation"""
        self._reset_environment()
        return self._get_observation()
    
    def step(self, action: Action) -> tuple[Observation, Reward, bool, Dict[str, Any]]:
        """Execute an action and return observation, reward, done flag, and info dict"""
        reward = Reward(total=0.0, feedback="No changes made")
        
        # Check for hallucination penalty first
        if not self._find_element(action.target_id):
            penalty_reward = Reward(
                total=PENALTY_HALLUCINATION,
                feedback=f"Hallucination penalty: Element '{action.target_id}' not found in current UI tree"
            )
            self.state.step_count += 1
            self.state.total_reward += penalty_reward.total
            info = {"state": self.state.model_dump()}
            return self._get_observation(), penalty_reward, self.state.is_complete, info
        
        # Check for invalid value penalty
        if not self._is_valid_value(action.value):
            penalty_reward = Reward(
                total=PENALTY_INVALID_VALUE,
                feedback=f"Invalid value penalty: '{action.value}' is empty or nonsensical"
            )
            self.state.step_count += 1
            self.state.total_reward += penalty_reward.total
            info = {"state": self.state.model_dump()}
            return self._get_observation(), penalty_reward, self.state.is_complete, info
        
        # Process normal actions
        if action.cmd == ActionType.PATCH_UI_ATTR:
            reward = self._handle_patch_ui_attr(action)
        elif action.cmd == ActionType.PATCH_UI_TEXT:
            reward = self._handle_patch_ui_text(action)
        elif action.cmd == ActionType.SYNC_BACKEND:
            reward = self._handle_sync_backend(action)
        
        self.state.step_count += 1
        self.state.total_reward += reward.total
        
        # Check if all tasks are completed
        all_complete = self._check_all_tasks_complete()
        self.state.is_complete = all_complete
        
        info = {"state": self.state.model_dump()}
        return self._get_observation(), reward, all_complete, info
    
    def _is_valid_value(self, value: Optional[str]) -> bool:
        """Check if a value is valid (not empty or nonsensical)"""
        if value is None:
            return False
        if isinstance(value, str):
            return len(value.strip()) > 0 and value.strip().lower() not in ["", "null", "none", "undefined"]
        return True
    
    def _calculate_partial_credit(self, target_value: str, provided_value: str, task_type: str) -> float:
        """Calculate partial credit for close but incorrectly formatted values"""
        if task_type == "medium":  # Price task
            # Extract numeric values for comparison
            import re
            target_num = re.findall(r'\d+\.?\d*', target_value)
            provided_num = re.findall(r'\d+\.?\d*', provided_value)
            
            if target_num and provided_num:
                target_float = float(target_num[0])
                provided_float = float(provided_num[0])
                
                # 50% credit if numeric value is correct but format is wrong
                if abs(target_float - provided_float) < 0.01:
                    return 0.5
        
        elif task_type == "hard":  # Material task
            # 50% credit if material name is correct but format is wrong
            target_material = target_value.replace("Material: ", "").strip().lower()
            provided_material = provided_value.replace("Material: ", "").strip().lower()
            
            if target_material == provided_material:
                return 0.5
        
        return 0.0
    
    def _handle_patch_ui_attr(self, action: Action) -> Reward:
        """Handle PATCH_UI_ATTR action"""
        element = self._find_element(action.target_id)
        if not element:
            return Reward(total=0.0, feedback=f"Element {action.target_id} not found")
        
        if action.key and action.value is not None:
            element["attributes"][action.key] = action.value
            
            # Check if this fixes the easy task (missing aria-label)
            if action.target_id == "buy-button" and action.key == "aria-label":
                if "easy" not in self.state.tasks_completed:
                    self.tasks["easy"].current_score = 1.0
                    self.state.tasks_completed.append("easy")
                    return Reward(
                        total=0.3,
                        accessibility=0.3,
                        feedback="Fixed missing aria-label on Buy button"
                    )
                else:
                    return Reward(total=0.0, feedback="Easy task already completed")
        
        return Reward(total=0.0, feedback="Attribute patched but no task completed")
    
    def _handle_patch_ui_text(self, action: Action) -> Reward:
        """Handle PATCH_UI_TEXT action"""
        element = self._find_element(action.target_id)
        if not element:
            return Reward(total=0.0, feedback=f"Element {action.target_id} not found")
        
        if action.value is not None:
            old_text = element["text"]
            element["text"] = action.value
            
            # Check if this fixes the medium task (price mismatch)
            if action.target_id == "price-display":
                correct_price = f"${self.backend_database['price']:.2f}"
                if action.value == correct_price:
                    if "medium" not in self.state.tasks_completed:
                        self.tasks["medium"].current_score = 1.0
                        self.state.tasks_completed.append("medium")
                        return Reward(
                            total=0.7,
                            data_integrity=0.7,
                            feedback="Fixed price mismatch between UI and backend"
                        )
                    else:
                        return Reward(total=0.0, feedback="Medium task already completed")
                else:
                    # Check for partial credit
                    partial_credit = self._calculate_partial_credit(correct_price, action.value, "medium")
                    if partial_credit > 0:
                        return Reward(
                            total=0.35,  # 50% of 0.7
                            data_integrity=0.35,
                            feedback=f"Partial credit: Correct price value but wrong format. Expected: {correct_price}"
                        )
            
            # Check if this fixes the hard task (material conflict)
            if action.target_id == "material-info":
                correct_material = f"Material: {self.backend_database['material']}"
                # Verify against material specs
                specs = self.material_specs.get(self.backend_database["product_id"], {})
                if specs.get("primary_material") == self.backend_database["material"]:
                    if action.value == correct_material:
                        if "hard" not in self.state.tasks_completed:
                            self.tasks["hard"].current_score = 1.0
                            self.state.tasks_completed.append("hard")
                            return Reward(
                                total=1.0,
                                semantic_accuracy=1.0,
                                feedback="Resolved material semantic conflict using specs verification"
                            )
                        else:
                            return Reward(total=0.0, feedback="Hard task already completed")
                    else:
                        # Check for partial credit
                        partial_credit = self._calculate_partial_credit(correct_material, action.value, "hard")
                        if partial_credit > 0:
                            return Reward(
                                total=0.5,  # 50% of 1.0
                                semantic_accuracy=0.5,
                                feedback=f"Partial credit: Correct material but wrong format. Expected: {correct_material}"
                            )
        
        return Reward(total=0.0, feedback="Text patched but no task completed")
    
    def _handle_sync_backend(self, action: Action) -> Reward:
        """Handle SYNC_BACKEND action"""
        # For this environment, sync_backend would sync UI to match backend
        element = self._find_element(action.target_id)
        if not element:
            return Reward(total=0.0, feedback=f"Element {action.target_id} not found")
        
        if action.target_id == "price-display":
            if "medium" not in self.state.tasks_completed:
                element["text"] = f"${self.backend_database['price']:.2f}"
                self.tasks["medium"].current_score = 1.0
                self.state.tasks_completed.append("medium")
                return Reward(
                    total=0.7,
                    data_integrity=0.7,
                    feedback="Synced price display with backend database"
                )
            else:
                return Reward(total=0.0, feedback="Medium task already completed")
        
        if action.target_id == "material-info":
            if "hard" not in self.state.tasks_completed:
                element["text"] = f"Material: {self.backend_database['material']}"
                self.tasks["hard"].current_score = 1.0
                self.state.tasks_completed.append("hard")
                return Reward(
                    total=1.0,
                    semantic_accuracy=1.0,
                    feedback="Synced material info with backend database"
                )
            else:
                return Reward(total=0.0, feedback="Hard task already completed")
        
        return Reward(total=0.0, feedback="Sync attempted but no task completed")
    
    def _find_element(self, element_id: str) -> Optional[Dict]:
        """Find an element by ID in the UI tree"""
        for page in self.frontend_ui_tree.values():
            for element in page.get("elements", []):
                if element["id"] == element_id:
                    return element
        return None
    
    def _check_all_tasks_complete(self) -> bool:
        """Check if all tasks are completed"""
        return len(self.state.tasks_completed) == len(self.tasks)
    
    def _get_observation(self) -> Observation:
        """Generate current observation"""
        ui_elements = []
        for page in self.frontend_ui_tree.values():
            for element_data in page.get("elements", []):
                ui_elements.append(UIElement(
                    id=element_data["id"],
                    tag=element_data["tag"],
                    text=element_data.get("text"),
                    attributes=element_data.get("attributes", {})
                ))
        
        # Generate screen reader summary
        screen_reader_text = self._generate_screen_reader_summary(ui_elements)
        
        return Observation(
            ui_elements=ui_elements,
            backend_record=self.backend_database.copy(),
            screen_reader_summary=screen_reader_text
        )
    
    def _generate_screen_reader_summary(self, ui_elements: List[UIElement]) -> str:
        """Generate what a screen reader would announce"""
        summary_parts = []
        
        for element in ui_elements:
            if element.tag == "button":
                aria_label = element.attributes.get("aria-label", element.text or "Button")
                summary_parts.append(f"Button: {aria_label}")
            elif element.tag == "span" and "price" in element.attributes.get("class", ""):
                summary_parts.append(f"Price: {element.text}")
            elif element.tag == "div" and "material" in element.attributes.get("class", ""):
                summary_parts.append(f"Material information: {element.text}")
            elif element.tag == "span" and "sku" in element.attributes.get("class", ""):
                summary_parts.append(f"Product code: {element.text}")
        
        return " | ".join(summary_parts) if summary_parts else "No readable content found"
    
    def get_tasks(self) -> List[TaskInfo]:
        """Get information about all available tasks"""
        return list(self.tasks.values())
    
    def get_state(self) -> EnvironmentState:
        """Get current environment state"""
        return self.state
    
    def grade(self) -> float:
        """Return overall grade (0.0 to 1.0) for the current episode"""
        if not self.state.is_complete:
            return 0.0
        
        total_weight = sum(task.reward_weight for task in self.tasks.values())
        weighted_score = sum(
            task.current_score * task.reward_weight 
            for task in self.tasks.values()
        )
        
        return weighted_score / total_weight if total_weight > 0 else 0.0

    def to_dict(self, obj):
        """Helper to convert dataclasses and nested objects to dictionaries for JSON"""
        if hasattr(obj, '__dataclass_fields__'):
            result = {}
            for field in obj.__dataclass_fields__:
                value = getattr(obj, field)
                result[field] = self.to_dict(value)
            return result
        elif isinstance(obj, list):
            return [self.to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {k: self.to_dict(v) for k, v in obj.items()}
        elif hasattr(obj, 'value'): # Handles Enums like ActionType
            return obj.value
        return obj