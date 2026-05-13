# controller/ui_loader.py

import importlib

def _import_ui(module_basename: str):
    last_exc = None
    for mod in (f"UI.{module_basename}", module_basename):
        try:
            return importlib.import_module(mod)
        except ModuleNotFoundError as e:
            last_exc = e
            continue
    if last_exc:
        raise last_exc
    raise ModuleNotFoundError(module_basename)

def _try_import_ui(module_basename: str):
    try:
        return _import_ui(module_basename).Ui_MainWindow
    except ModuleNotFoundError:
        return None

# UI classes
Ui_AdminLogin = _try_import_ui("AdminLogin_ui")
Ui_AdminDashboard = _try_import_ui("AdminDashboard_ui")
Ui_AdminManagement = _try_import_ui("adminManagement_ui")
Ui_AdminReports = _try_import_ui("adminReports_ui")

Ui_RegistrarLogin = _try_import_ui("registrarLogin_ui")
Ui_CreateAccount = _try_import_ui("createAccount_ui")
Ui_RegistrarDashboard = _try_import_ui("registrarDashboard_ui")
Ui_EnrollmentDashboard = _try_import_ui("enrollmentDashboard_ui")
Ui_ManagementDashboard = _try_import_ui("managementDashboard_ui")
Ui_Payment = _try_import_ui("payment_ui")
Ui_Slots = _try_import_ui("slots_ui") # <--- ADDED SLOTS UI

Ui_STEM11 = _try_import_ui("stem11_ui")
Ui_STEM12 = _try_import_ui("stem12_ui")
Ui_ABM11 = _try_import_ui("ABM11_ui")
Ui_ABM12 = _try_import_ui("ABM12_ui")
Ui_HUMSS11 = _try_import_ui("HUMSS11_ui")
Ui_HUMSS12 = _try_import_ui("HUMSS12_ui")
Ui_GAS11 = _try_import_ui("GAS11_ui")
Ui_GAS12 = _try_import_ui("GAS12_ui")
Ui_TVL11 = _try_import_ui("TVL11_ui")
Ui_TVL12 = _try_import_ui("TVL12_ui")

Ui_EnrollmentReports = _try_import_ui("enrollmentReports_ui")