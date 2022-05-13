#####
Notes
#####


***************
systemd history
***************

- http://0pointer.de/blog/projects/systemd.html
- https://thenewstack.io/unix-greatest-inspiration-behind-systemd/
- https://lwn.net/Articles/777595/
- https://blog.darknedgy.net/technology/2020/05/02/0/


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


*************
Miscellaneous
*************

- Others also recommend ``systemd-nspawn``.

    "As an aside, we recommend using a more intelligent, modern tool like systemd-nspawn instead."

    -- https://github.com/purpleidea/docker/commit/445197336ebfc341fe1c922410324422b5722328

- If you need to...

    ok if you need nested containers inside an alpine container on github actions, here is how you do it:

    - https://twitter.com/ariadneconill/status/1502406979427446787
    - https://github.com/chainguard-dev/melange/blob/main/.github/workflows/e2e.yaml#L13-L14

    ::

        jobs:
          build:
            name: bootstrap package
            runs-on: ubuntu-latest
            container:
              image: alpine:latest
              options: |
                --cap-add NET_ADMIN --cap-add SYS_ADMIN --security-opt seccomp=unconfined --security-opt apparmor:unconfined


- https://de.wikipedia.org/wiki/Liste_von_Virtualisierungsprodukten
