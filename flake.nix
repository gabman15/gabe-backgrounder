{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
  };
  outputs = { nixpkgs, ... }@inputs: {
    packages.x86_64-linux = let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in rec {
      gabe-backgrounder = pkgs.callPackage ./package.nix {};
      default = gabe-backgrounder;
    };
  };
}
