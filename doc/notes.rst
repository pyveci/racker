#####
Notes
#####


*********
Multiarch
*********

CHANGES WITH 250:

    * The GPT image dissection logic in systemd-nspawn/systemd-dissect/…
      now is able to decode images for non-native architectures as well.
      This allows systemd-nspawn to boot images of non-native architectures
      if the corresponding user mode emulator is installed and
      systemd-binfmtd is running.

      -- https://lwn.net/Articles/879739/
      -- https://github.com/systemd/systemd/blob/main/NEWS

    - https://0pointer.net/blog/the-wondrous-world-of-discoverable-gpt-disk-images.html
