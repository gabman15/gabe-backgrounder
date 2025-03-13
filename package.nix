{ python3Packages }:

with python3Packages;
buildPythonApplication {
  pname = "gabe-backgrounder";
  version = "1.0";
  src = ./.;
}
